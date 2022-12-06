import time

import helper
import profile_tool

start_time = time.time()
DoCoverageTest = False

if DoCoverageTest:
    import coverage

    cov = coverage.Coverage()
    cov.start()


helper.LoadMap("outputmap/basemap/basemap_wireframe.scx")
helper.EP_SetRValueStrictMode(True)

helper.InitialWireframe.wireframes("Terran Marine", "Protoss Archon")
helper.InitialWireframe.wireframes("Terran Goliath", "Terran Dropship")
helper.InitialWireframe.wireframes("Devouring One", "Zerg Hive")
helper.InitialWireframe.wireframes("Zerg Queen's Nest", "Protoss Photon Cannon")
helper.InitialWireframe.wireframes("Protoss Scout", "Psi Emitter")
helper.InitialWireframe.wireframes("Protoss Cybernetics Core", "Protoss Probe")


@helper.TestInstance
def test_wireframe():
    helper.SetWireframes("Terran SCV", "Zerg Drone")


helper.CompressPayload(True)
helper.ShufflePayload(False)

# profile_tool.profile(f, "profile.json")
helper.SaveMap("outputmap/test_wireframe.scx", helper._testmain)
print("--- %s seconds ---" % (time.time() - start_time))

if DoCoverageTest:
    cov.stop()
    cov.html_report(include=["C:\\gitclones\\eudtrglib\\eudplib\\*"])
