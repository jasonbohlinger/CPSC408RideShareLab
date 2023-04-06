from helper import helper
from db_operations import db_operations

db_ops = db_operations() # Insert db file here
#data = helper.data_cleaner() # Insert csv file here

def startScreen():
    print('Welcome to RideShare.')
    print('''
    Are you a new user?
    0. No
    1. Yes
    ''')
    isNewUser = bool(helper.get_choice([0, 1]))
    user_status = 0 # Initializing value for if statement below
    userID = 0 # Initializing value for scope
    if (isNewUser):
        user_status = create_new_user()
    else:
        while(True):
            userID = input('Enter your user ID: \n')
            while True:
                try:
                    userID = int(userID)       
                except ValueError:
                    print("Not an integer! Try again.")
                    continue
                else:
                    break
            # user status:
            # 0. Not found in database
            # 1. Rider
            # 2. Driver
            if userID in get_riderIDs():
                user_status = 1
                break
            elif userID in get_driverIDs():
                user_status = 2
                break
            else:
                user_status = 0
                print('Your userID is not connected to a current rider or driver. Try again, or exit to create a new profile.')
    
    if (user_status == 1):
        display_rider_options(userID)
    else:
        display_driver_options(userID)

def create_new_user():
    print('''
    Which type of profile would you like to create:
    1. Rider
    2. Driver
    ''')
    profileType = helper.get_choice([1, 2])
    if (profileType == 1):
        while True:
            riderID = input('What is your new rider ID? (integer) \n')
            try:
                riderID = int(riderID)
            except ValueError:
                print("Not an integer! Try again.")
                continue
            else:
                if (riderID in get_riderIDs() or riderID in get_driverIDs()):
                    print("This ID number is already used by another user. Try again.")
                    continue
                break

        query = '''
        INSERT INTO riders VALUES (
            %s
        );
        '''
        values = [riderID]
        db_ops.name_placeholder_query(query, values)
        db_ops.commit()
        
    else:
        while True:
            driverID = input('What is your new driver ID? (integer) \n')
            try:
                driverID = int(driverID)       
            except ValueError:
                print("Not an integer! Try again.")
                continue
            else:
                if (driverID in get_riderIDs() or driverID in get_driverIDs()):
                    print("This ID number is already used by another user. Try again.")
                    continue
                break
        query = '''
        INSERT INTO drivers VALUES(
            %s,
            0,
            0
        );
        '''
        values = [driverID]
        db_ops.name_placeholder_query(query, values)
        db_ops.commit()
    return profileType

# Display rider options
def display_rider_options(riderID):
    print('''
    RIDER MENU
    Enter the number for one of the following options: 
    1. View rides
    2. Find a driver
    3. Rate my driver
    ''')
    # 1 and 3 are done
    user_choice = helper.get_choice([1, 2, 3])
    match user_choice:
        case 1:
            view_rides_rider(riderID)
        case 2:
            find_driver(riderID)
            display_rider_options(riderID)
        case 3:
            rate_latest_driver(riderID)

# Display driver options
def display_driver_options(driverID):
    print('''
    DRIVER MENU
    Enter the number for one of the following options:
    1. View rating
    2. View rides
    3. Activate driver mode
    4. Deactivate driver mode
    ''')
    # 1, 2, 3, and 4 are all done
    user_choice = helper.get_choice([1, 2, 3, 4])
    match user_choice:
        case 1:
            getDriverRating(driverID)
        case 2:
            view_rides_driver(driverID)
        case 3:
            update_driver_status(driverID, 1)
            print('Driver is active')
        case 4:
            update_driver_status(driverID, 0)
            print('Driver is NOT active')

# return list of all riderIDs
def get_riderIDs():
    query = '''
    SELECT *
    FROM riders;
    '''
    return db_ops.single_attribute(query)

# return list of all driverIDs
def get_driverIDs():
    query = '''
    SELECT driverID
    FROM drivers;
    '''
    return db_ops.single_attribute(query)

# return list of all rideIDs
def get_latest_rideID():
    query = '''
    SELECT MAX(rideID)
    FROM rides;
    '''
    return db_ops.single_attribute(query)[0]

# method responsible for getting input and returning 
def getDriverRating(driverID):
    query = '''
    SELECT rating
    FROM drivers
    where driverID = %s;
    '''
    values = [driverID]

    rating = db_ops.name_placeholder_query(query, values)[0][0]

    print("Driver #", driverID, " has a rating of: ", rating)


def rate_latest_driver(riderID):
    query = '''
            SELECT MAX(rideID)
            FROM rides
            WHERE riderID = %s
            '''
    latest_ride_id = db_ops.name_placeholder_query(query, [riderID])[0][0]
    if (latest_ride_id == None):
        print('No rides found for this user.')
        return

    print('Latest_ride_id: ', latest_ride_id)
    while(True):
        query = '''
        SELECT *
        FROM rides
        WHERE rideID = %s
        '''
        results = db_ops.name_placeholder_query(query, [latest_ride_id])
        helper.pretty_print_rides(results)
        print('''
        Is this the correct ride?
        1. Yes
        2. No
        ''')
        user_choice = helper.get_choice([1, 2])
        if user_choice == 1:
            this_ride_driver_id = results[0][2]
            print('Driver ID: ', this_ride_driver_id)
            break
        else:
            while True:
                latest_ride_id = input('Enter the rideID you want to rate the driver for: \n')
                try:
                    latest_ride_id = int(latest_ride_id)       
                except ValueError:
                    print("Not an integer! Try again.")
                    continue
                else:
                    # check that the new ride id includes the rider we are looking at
                    query = '''
                    SELECT riderID
                    FROM rides
                    WHERE rideID = %s
                    '''
                    results = db_ops.name_placeholder_query(query, [latest_ride_id])
                    if (len(results) == 0):
                        print('This ride does not exist. Try again.')
                        continue
                    this_rider_id = results[0][0]
                    if (this_rider_id != riderID):
                        print('You were not a part of this ride. Try again with another rideID')
                        continue
                    break
    while True:
        new_driver_rating = input('Enter the driver rating for this ride: \n')
        try:
            new_driver_rating = float(new_driver_rating)       
        except ValueError:
            print("Not a float! Try again.")
            continue
        else:
            break
    curr_driver_rating = get_driver_rating(this_ride_driver_id)
    new_driver_rating = (curr_driver_rating + new_driver_rating) / 2

    query = '''
    UPDATE drivers
    SET rating = %s
    WHERE driverID = %s
    '''
    db_ops.name_placeholder_query(query, [new_driver_rating, this_ride_driver_id])
    db_ops.commit()
    print('Successfully updated driver rating')
    
def find_driver(riderID):
    print()
    # find available driver
    active_driver_id = get_active_drivers()
    if (len(active_driver_id) == 0):
        print('No available drivers. Try again later.')
        return
    active_driver_id = active_driver_id[0]
    # ask rider for PU/DO info
    pickup_loc = input('Enter the pick up location:\n')
    dropoff_loc = input('Enter the drop off location:\n')

    # create the ride entry and give rideID to user
    query = '''
    INSERT INTO rides
    VALUES(
    %s, %s, %s, %s, %s
    );
    '''
    last_ride_id = get_latest_rideID()
    if (last_ride_id == None):
        last_ride_id = 0
    new_ride_id = last_ride_id + 1
    values = [new_ride_id, riderID, active_driver_id, pickup_loc, dropoff_loc]
    db_ops.name_placeholder_query(query, values)
    db_ops.commit()
    print('Your new ride ID: ', new_ride_id)


def get_driver_rating(driverID):
    while(True):
        query = '''
        SELECT rating
        FROM drivers
        WHERE driverID = %s
        '''
        results = db_ops.name_placeholder_query(query, [driverID])
        if (len(results) == 0):
            print('Could not find driver with that ID. Try again:\n')
            while True:
                driverID = input('Enter a new driver ID: ')
                try:
                    driverID = int(driverID)       
                except ValueError:
                    print("Not an integer! Try again.")
                    continue
                else:
                    break
        else:
            return results[0][0]

# gets information of all rides given by particular dID
def view_rides_rider(riderID):
    query = '''
    SELECT *
    FROM rides
    WHERE riderID = %s;
    '''
    values = [riderID]
    results = db_ops.name_placeholder_query(query,values)
    if (len(results) == 0):
        print('No rides found for this user')
    else:
        helper.pretty_print_rides(results)


def view_rides_driver(driverID):
    query = '''
    SELECT *
    FROM rides
    WHERE driverID = %s;
    '''
    values = [driverID]
    results = db_ops.name_placeholder_query(query,values)
    if (len(results) == 0):
        print('No rides found for this user.')
    else:
        helper.pretty_print_rides(results)

# returns list of driverIDs that are currently active
def get_active_drivers():
    query = '''
    SELECT driverID
    FROM drivers
    WHERE isDriving = 1;
    '''

    return db_ops.single_attribute(query)

def update_driver_status(driverID, newStatus):
    query = '''
        UPDATE drivers
        SET isDriving = %s
        WHERE driverID = %s
    '''
    values = [newStatus, driverID]
    db_ops.name_placeholder_query(query, values)
    db_ops.commit()

def is_empty():
    num_empty = 0
    rideQuery = '''
    SELECT COUNT(*)
    FROM rides
    '''
    num_empty += db_ops.single_record(rideQuery)
    
    riderQuery = '''
    SELECT COUNT(*)
    FROM riders
    '''
    num_empty += db_ops.single_record(riderQuery)

    driversQuery = '''
    SELECT COUNT(*)
    FROM drivers
    '''
    num_empty += db_ops.single_record(driversQuery)

    return num_empty == 0

# def pre_process():
#     if is_empty():
#         attribute_count = len(data[0])
#         placeholders = ("?,"*attribute_count)[:-1]
#         query = "INSERT INTO 

startScreen()
    