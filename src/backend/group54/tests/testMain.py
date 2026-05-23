import unittest

import auxiliaryFunctionsTests
import cacheMaintainanceTests
import wikidataQueryingTests

auxiliaryFunctions = unittest.TestLoader().loadTestsFromModule(auxiliaryFunctionsTests)

cacheMaintainance = unittest.TestLoader().loadTestsFromModule(cacheMaintainanceTests)

wikidataQuerying = unittest.TestLoader().loadTestsFromModule(wikidataQueryingTests)

unittest.TextTestRunner(verbosity=2).run(auxiliaryFunctions)
unittest.TextTestRunner(verbosity=2).run(cacheMaintainance)
# unittest.TextTestRunner(verbosity=2).run(queries)
unittest.TextTestRunner(verbosity=2).run(wikidataQuerying)
