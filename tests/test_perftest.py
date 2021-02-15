import helper


from perftests import (
    # testbasic,
    testmemio,
    # testbubblesort,
)

# helper.CompressPayload(True)
helper.test_runall("perf")
