import time
import helper

start_time = time.time()
DoCoverageTest = False

if DoCoverageTest:
    import coverage

    cov = coverage.Coverage()
    cov.start()


helper.LoadMap("outputmap/basemap/basemap_wireframe.scx")
helper.EP_SetRValueStrictMode(True)

with open("outputmap/basemap/RequireData", "rb") as reqfile:
    helper._add_datadumper(reqfile.read(), [0x58D740], set(["copy"]))

helper.CompressPayload(True)
helper.ShufflePayload(False)

# profile_tool.profile(f, "profile.json")
helper.SaveMap("outputmap/test_datadumper.scx", helper._testmain)
print("--- %s seconds ---" % (time.time() - start_time))

if DoCoverageTest:
    cov.stop()
    cov.html_report(include=["C:\\gitclones\\eudtrglib\\eudplib\\*"])
