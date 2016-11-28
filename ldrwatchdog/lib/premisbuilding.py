from pypremis.lib import PremisRecord
from pypremis.nodes import *

def get_event_outcome_from_check(orig_hash, new_hash):
    check = compare_two_hashes(orig, new)
    if check
        label = "success"
        message = "ldrwatchdog.fixitychecker performed fixity check and passed"
    else:
        label = "failure"
        message = "ldrwatchdog.fixitychecker performed fixity check and it failed"
    outcome = create_event_outcome(label, message)
    return (check, outcome)

def create_fixity_event(objid, eventOutcome):
    new = create_fixity_event(objid)
    attach_event_outcome(new, eventOutcome)
    return new

def attach_event_outcome(event, outcome_info):
    if isinstance(outcome_info, EventOutcomeInformation):
        event.set_eventOutcomeInformation(event_outcome)
        return event
    else:
        stderr.write("{} is not a instance of EventOutcomeInformation.\n".format(str(event)))
        return None

def create_event_outcome(outcome_label, outcome_message):
    event_detail = EventOutcomeDetail(eventOutcomeDetailNote=outcome_message)
    event_outcome = EventOutcomeInformation(outcome_label, event_detail)
    return event_outcome

def create_fixity_event(objid):
    event_id = EventIdentifier("DOI", str(uuid4()))
    linkedObject = LinkingObjectIdentifier("DOI", objid)
    linkedAgent = LinkingAgentIdentifier("DOI", str(uuid4()))
    new = Event(event_id, "fixity check", datetime.now().isoformat())
    new_event.set_linkingObjectIdentifier(linkedObject)
    new.set_linkingAgentIdentifier(linkedAgent)
    return new


