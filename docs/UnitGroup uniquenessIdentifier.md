# 유닛그룹에 uniquenessIdentifier 추가하기

## Motivation

UnitGroup에 저장된 유닛이 죽고 다른 유닛이 해당 인덱스를 채우는 상황을 방지하려면 현재로서는 UnitGroup.cploop를 매 프레임 실행해서 cunit.dying이나 cunit.remove를 실행해야만 한다.

저장된 유닛이 죽고 새 유닛이 해당 인덱스를 채우면 스타크래프트에서 CUnit의 0xA5 uniquenessIdentifier를 1 증가하니까, UnitGroup.add에서 uniquenessIdentifier도 저장해서 조건에 비교하는 방법으로 기존 유닛인지 새 유닛이 대체한건지 판별할 수 있다.

## 장점
UnitGroup이 고장나지 않으려고 .cploop를 매 프레임 실행할 필요가 없어짐
그룹 순회를 매 프레임 돌리지 않는 게 성능적으로도 큰 이득이고, 버그를 방지한다는 점에서 괜찮은 교환임

## 단점
- UnitGroup.add의 비용 증가 : 0xA5 uniquenessIdentifier도 읽어야함 (기존 : 1트리거 생성, 3트리거 10액션 실행 -> EUDFunc으로 바꿔야함)
- cunit.remove의 비용 증가 : 배열 2개를 비워야 함

## 의문점 1
다른 유닛이 CUnit을 채워서 삭제할 때 유저 코드를 실행할 수 있게 해야하나?
```js
foreach(cunit : UnitGroup.cploop) {
    foreach(removed : cunit.remove_event) {
        
    }
    foreach(dead : cunit.dying) {

    }
}
```
### 대안 1 : 모든 유닛 그룹 삭제에서 cunit.dying 블럭이 실행되게 한다
dead는 원래 죽는 중인 유닛인데, dead가 기존 유닛을 교체한 새 유닛도 접근하게 되면 의미가 이상해진다.

### 대안 2 : 모르겠다 일단 빼고 출시하고 나중에 생각하죠? ^^

## 구현

### UnitGroup.add 구현
UnitGroup가 추가로 EUDVArray(capacity)() 를 가진다.
(UnitGroup.id_varray)
UnitGroup.loopvar와 유사하게, 조건 대입 용 변수도 추가한다.
(UnitGroup.idvar)

### 의문점 2
기존의 EUDVArray를 2 * capacity로 늘리고, epd와 uniquenessIdentifier를 교차로 저장하기
vs.
별도의 EUDVArray(capacity)에 저장하기

현재로선 후자가 나음
EUDVArray(size)(dest=목적지 초기값, nextptr=다음 트리거 초기값) 은 배열 전체에 적용되고 배열 멤버마다 초기값을 다르게 할 수 없음.

### UnitGroup.cploop.__iter__ 구현
```py
# 초기화
idvar의 다음 트리거와 목적지를 초기화한다.
idvar.SetDest(EPD(CheckID + 8))
SetNextPtr(idvar.GetVTable(), self._parent.varray)

# UnitGroup의 추가 순서는 뒤에서 앞으로
# UnitGroup의 순회 순서는 앞에서 뒤으로
if _UnsafeWhileNot()(UnitGroup의 맨 뒤에 도달):
    트리거 실행 순서
    1. block["loopstart"] : UnitGroup의 끝까지 순회했는지 체크
    2. id_varray : idvar에 id값 복사
    3. idvar : id값을 조건 CheckID의 값 칸에 대입
    4. varray : loopvar에 epd 복사
    5. loopvar : epd를 0x6509B0 (CP트릭)에 대입
    ** loopvar의 초기값은 epd + 0xA5/4 가 된다 **
    6. CheckID : id가 다르면 UnitGroup에서 제거
    7. CheckDeaths : (명령 0인 죽은 유닛이나, 체력 0 좀비 유닛 제거)

    block["loopstart"]의 다음 트리거는 id_varray
    id_varray는 EUDVArray(capacity)(dest=self.idvar, nextptr=self.idvar.GetVTable())
    -> id_varray내 변수 트리거들의 다음 트리거는 idvar
    저장된 id 값을 idvar에 복사한다.

EUDEndWhile()
```

### cunit.remove 구현
