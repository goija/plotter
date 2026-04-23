import sys
import os
# Voeg src toe aan pad
sys.path.append(os.path.join(os.getcwd(), "datapipe_ccw_bundle/src"))

from datapipe.config import load_config
from datapipe.normalize.daily import normalize_day
from datapipe.debruijn.states import build_reference_states
from datapipe.model.disturbance import build_daily_disturbance
from datapipe.model.score import score_day
from datapipe.publish.report import publish_day

date = "2024-05-20"
cfg = load_config()

print("START: Handmatige afronding na KNMI...")
normalize_day(date, cfg)
print("SUCCESS: normalize completed")
build_reference_states(cfg)
print("SUCCESS: state build completed")
build_daily_disturbance(date, cfg)
print("SUCCESS: disturbance build completed")
score_day(date, cfg)
print("SUCCESS: scoring completed")
publish_day(date, cfg)
print("SUCCESS: publish completed")