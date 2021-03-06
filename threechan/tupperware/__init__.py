### SETUP

# Imports
import datetime
from flask import Blueprint, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
import os

# Twilio account info
account_sid = 'ACf507d665804b1ccb4962e2bdc0390c48'
auth_token = os.environ['TWILIO_AUTH_TOKEN']

# Phone numbers
admin_number = '17755713503'
front_numbers = ['+17755716730', '+17755715833', '+17755718918', '+17755715738',
                     '+17755713457', '+17755718401', '+17755714365', '+17755716227', '+17755718057',
                     '+17755717604', '+17755717317', '+17755713586', '+17755718734', '+17755716175',
                     '+17755719751', '+17755718902', '+17755718902', '+17755718070', '+17755714535',
                     '+17755714535', '+17755719714']
# Us!
gideon_cell = '+14159393751'
andrea_cell = '+14155496087'
lexi_cell = '+14088887272'
miju_cell = '+14152655604'
peter_cell = '+14155099881'
app_admins = [gideon_cell, andrea_cell, lexi_cell, miju_cell, peter_cell]

# Other global constants
twilio_client = Client(account_sid, auth_token)
flask_blueprint = Blueprint('flask_blueprint', __name__)
test_message_body = "Hello from Tupperware 2018! The time is %s" % str(datetime.datetime.now())

### END SETUP

### DB

# Update
def update_participant_number_allocations(participant, front, admin):
    from threechan.models import Allocation, db
    new_alloc = Allocation(participant, front, admin)
    db.session.add(new_alloc)
    db.session.commit()
    return new_alloc
def clear_participant_number_allocations():
    from threechan.models import Allocation, db
    db.session.query(Allocation).delete()
    db.session.commit()

# Access
def front_num_for_participant(participant_number):
    from threechan.models import Allocation, db
    try:
        alloc = db.session.query(Allocation).filter(Allocation.participant_number==participant_number).one()
        return alloc.front_number
    except:
        return None
def admin_for_participant(participant_number):
    from threechan.models import Allocation, db
    try:
        alloc = db.session.query(Allocation).filter(Allocation.participant_number==participant_number).one()
        return alloc.participant_number
    except:
        return None
def allocation_for_participant(participant_number):
    from threechan.models import Allocation, db
    alloc = None
    try:
        alloc = db.session.query(Allocation).filter(Allocation.participant_number==participant_number).one()
    except:
        pass
    return alloc
def allocation_for_front_number(front_number):
    from threechan.models import Allocation, db
    try:
        alloc = db.session.query(Allocation).filter(Allocation.front_number==front_number).one()
        return alloc
    except:
        return None
def all_tuples():
    from threechan.models import Allocation, db
    tuples = []
    for alloc in db.session.query(Allocation).all():
        tuples.append((alloc.participant_number, alloc.front_number, alloc.admin_number))
    return tuples

### END DB

### APP ROUTES

# Admin - insert number
@flask_blueprint.route('/admin_insert_number', methods=['GET', 'POST'])
def admin_insert_number():
    # Get info from incoming request, prepare response object
    message_data = request.form
    if 'From' not in message_data:
        return("I'm the default test response for the admin insert route.")
    from_number = message_data['From']
    if from_number not in app_admins:
        non_admin_response = MessagingResponse()
        non_admin_response.message("We don't know how you did this, but we planned for it anyway - no joy for you!")
        return str(non_admin_response)
    body = message_data['Body']
    admin_insert_response = MessagingResponse()

    ### INPUT TYPES

    # Is it a request to view the list of allocations?
    if body == "Allocations":
        tuples = all_tuples()
        allocations_str = ""
        for tuple in tuples:
            allocations_str += "P: %s, F: %s, A: %s\n" % (tuple[0], tuple[1], tuple[2])
        admin_insert_response.message("""The current list of allocations is:\n\n%s""" % str(all_tuples()))
        return str(admin_insert_response)

    # Is it a request to wipe all allocations?
    if body == "WIPE ALLOCATIONS FOR REAL":
        admin_insert_response.message("Ok, WIPING ALL ALLOCATIONS! Hope you meant it ;)")
        clear_participant_number_allocations()
        return str(admin_insert_response)

    # Finally, assume it's intended to be a participant number.
    
    # Didn't receive valid participant number?
    if len(body) != 10 or not body.isdigit():
        admin_insert_response.message("Received body \"%s\" which is not a valid ten-digit participant number." % body)
        return str(admin_insert_response)

    # Received participant number
    participant_number = '+1%s' % body

    # New participant? Handle if possible
    from threechan.models import Allocation, db
    existing_alloc = allocation_for_participant(participant_number)
    if not existing_alloc:
        # Any numbers left?
        for possible_front_num in front_numbers:
            existing_front_alloc = allocation_for_front_number(possible_front_num)
            if not existing_front_alloc:
                # Found one!
                existing_alloc = update_participant_number_allocations(participant_number,
                                                                           possible_front_num,
                                                                           from_number)
                break
            
    # No front numbers left? :(
    print("Existing alloc %s for participant number %s" % (existing_alloc, participant_number))    
    if not existing_alloc:
        admin_insert_response.message("""No front numbers left to allocate for participant number %s :(.\
        Please ask Gideon to add functionality to the app.""" % participant_number)
    # We made an allocation - inform the admin who messaged in
    else:
        allocated_front_num = front_num_for_participant(participant_number)
        admin_insert_response.message("""New allocation made! You (admin %s) are now able to message participant %s\
        via front number %s. Go forth and make art.""" % (from_number, participant_number, allocated_front_num))
        admin_insert_response.message(allocated_front_num)

    return str(admin_insert_response)

# Admin - incoming call
@flask_blueprint.route('/admin_incoming_call', methods=['GET', 'POST'])
def admin_incoming_call():
    # Start our voice response
    resp = VoiceResponse()

    # Read a message aloud to the caller
    resp.say("We don't know how you did this. But we planned for it anyway. No joy for you.", voice='alice')

    return str(resp)

# Incoming SMS - to front number
@flask_blueprint.route('/front_incoming_sms', methods=['GET', 'POST'])
def front_incoming_sms():
    # Get info from incoming request, prepare response object
    message_data = request.form
    if 'From' not in message_data or 'To' not in message_data:
        return("I'm the default test response for the admin insert route.")
    from_number = message_data['From']
    to_number = message_data['To']
    body = message_data['Body']

    # Find the allocated admin and participant for this front number
    allocated_admin, participant = None, None
    front_alloc = allocation_for_front_number(to_number)
    if front_alloc:
        allocated_admin = front_alloc.admin_number
        participant = front_alloc.participant_number

    # Was this from an admin?
    if from_number in app_admins:
        
        # Was it the allocated admin? If so, pass their message along and let them know.
        if from_number == allocated_admin:
            # Response for admin
            admin_message_response = MessagingResponse()
            admin_message_response.message("ADMIN: SUCCESS - SENDING YOUR MESSAGE ALONG TO %s." % participant)
            # Message to participant
            message_to_participant = twilio_client.messages.create(
                from_=to_number,
                body=body,
                to=participant)
            return str(admin_message_response)

        # Otherwise, we'll implement admin switching eventually.
        else:
            admin_message_response = MessagingResponse()
            admin_message_response.message("""Sorry, the allocated admin for that front number isn't you - it's\
            %s. Use their phone for this conversation.""" % (allocated_admin))
            return str(admin_message_response)

    # Or was it from the participant?
    elif from_number == participant:
        # Pass it along to the allocated admin
        str_to_return = """RESPONSE RECEIVED FROM %s:
        %s""" % (from_number, body)
        message_to_admin = twilio_client.messages.create(
            from_=to_number,
            body=str_to_return,
            to=allocated_admin)
        return message_to_admin.body

    # Or was it from none of the above?
    else:
        print("From number: %s, participant number: %s" % (from_number, participant_number))
        anon_response_message = "How did you even get this number...?"
        anon_response = MessagingResponse()
        anon_response.message(anon_response_message)
        return str(anon_response_message)

# Incoming call - to front number
@flask_blueprint.route('/front_incoming_call', methods=['GET', 'POST'])
def front_incoming_call():
    # Get info from incoming request, prepare response object
    message_data = request.form
    if 'From' not in message_data or 'To' not in message_data:
        return("I'm the default test response for the admin insert route.")
    from_number = message_data['From']
    to_number = message_data['To']

    # Find the allocated admin and participant for this front number
    allocated_admin, participant = None, None
    front_alloc = allocation_for_front_number(to_number)
    if front_alloc:
        allocated_admin = front_alloc.admin_number
        participant = front_alloc.participant_number

    # Start our voice response
    resp = VoiceResponse()

    # Was it the participant?
    if from_number == participant:
        # Read a message aloud to the caller
        resp.say("L O L O L O L O L O L O L. Of course I blocked you from calling me you idiot.", voice='alice')

    # Was it the allocated admin?
    elif from_number == allocated_admin:
        resp.say("Now routing your call to the participant.")
        resp.dial(participant, callerId=to_number)

    # Or, was it a random person?
    else:
        resp.say("We don't know how you did this, but we planned for it anyway - no joy for you!")

    return str(resp)

# Test message for Gideon
@flask_blueprint.route('/test_message_gid')
def test_message_gid():
    message = twilio_client.messages.create(
        to=gideon_cell,
        from_=admin_number,
        body=test_message_body)
    return "Message SID: %s" % message.sid

### END APP ROUTES


