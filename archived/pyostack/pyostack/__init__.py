from compute import Compute
from identity import Identity
from metering import Metering

import ConfigParser
import os


def init(conffile):
    if not os.path.exists(conffile):
        raise RuntimeError("Config file %s not found" % conffile)
    conf = ConfigParser.SafeConfigParser()
    conf.read([conffile])
    return conf
