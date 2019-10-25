#include <stdio.h>
#include <time.h>

extern "C"
{
    const char *compileString(
        const char *modname,
        const char *rawcode);
    void freeCompiledResult(const char *str);
}

auto source = ""
              "import tile;\n"
              "import loc;\n"
              "\n"
              "function inBounds(x, y) {\n"
              "    return (x < 8 && y < 8) ? 1 : 0;\n"
              "}\n"
              "\n"
              "function canPieceGoTo(player, x, y) {\n"
              "    if(!inBounds(x, y)) return 0;\n"
              "    if (tile.tile(x, y) == 0 || tile.tile(x, y).player != player) {\n"
              "        return 1;\n"
              "    }\n"
              "    else return 0;\n"
              "}\n"
              "\n"
              "function placeScourge(player, x, y) {\n"
              "    loc.move1x1Loc(x, y);\n"
              "    CreateUnit(1, 'Zerg Scourge', '1x1', player);\n"
              "}\n"
              "\n"
              "\n"
              "function isTileOwnedBy(x, y, player) {\n"
              "    const piece = tile.tile(x, y);\n"
              "    if(!piece) return false;\n"
              "    if(piece.player == player) return true;\n"
              "    else return false;\n"
              "}\n"
              "\n"
              "\n"
              "/**\n"
              " * Common function for queen, rook and bishop.\n"
              " */\n"
              "function getQRBPossibleDestination(dxTable: EUDArray, dyTable: EUDArray, dirn, player, x, y) {\n"
              "    var dx, dy;\n"
              "    for(var direction = 0 ; direction < dirn ; direction++) {\n"
              "        dx, dy = dxTable[direction], dyTable[direction];\n"
              "        var x1, y1 = x + dx, y + dy;\n"
              "\n"
              "        while(inBounds(x1, y1)) {\n"
              "            if(tile.tile(x1, y1) == 0) placeScourge(player, x1, y1);\n"
              "            else if(tile.tile(x1, y1).player != player) {\n"
              "                placeScourge(player, x1, y1);\n"
              "                break;\n"
              "            }\n"
              "            else break;\n"
              "            x1 += dx;\n"
              "            y1 += dy;\n"
              "        }\n"
              "    }\n"
              "}";

int main()
{
    int start = clock();
    printf("Compiling 1000 times - ");
    for (int i = 0; i < 1000; i++)
    {
        auto compiled = compileString("main", source);
        freeCompiledResult(compiled);
    }
    printf("%lums\n", clock() - start);
}
