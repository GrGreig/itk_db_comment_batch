""""Program to add comments to a list of batches of sensors. Developed for the Vancouver
cluster to quickly attach import information to all sensors of a batch shipment.

Note: This module depends on having an up to date inventory CSV file. This can be generated
with the inventory2CSV.py script. Done with the command:
    
python inventory2CSV.py --project S 
                        --componentType SENSOR 
                        --currentLocation <location> 
                        --properties -1 
                        --outfile <output_file_name>
                        --write serialNumber
                        
Note: Until itk_pdb is pip installable, this should be saved directly to the 
'production_database_scripts' directory."""

import argparse
import os
import sys
import itk_pdb.dbAccess as dbAccess

INVENTORY_FILENAME = 'sensor_inventory.csv'


def get_inventory_info(inventory_filename):
    """Opens the inventory file and retrives lists of the 'serial_numbers', 'dates_recieved' and 'ids'.
    Assumes that the inventory update file has been called correctly and that data is in the format:
    
    [Serial Number, Date Recieved, ID]
    
    Removes any components with type 'None' in the date or id column. 
    
    Returns each as a list."""
    with open(inventory_filename, 'r') as file:
        data = file.read()
    rows = data.splitlines()
    serial_nums, dates, batch_nums = ([] for i in range(3))
    for row in rows[2:]:
        serial_num, date, id = row.split(',')
        if date != 'None' and id != 'None':
            serial_nums.append(serial_num)
            dates.append(date)
            batch_nums.append(id.split('-')[0])
    return serial_nums, dates, batch_nums

def check_batches(inventory_batches, comment_batches):
    """Checks if the batch is in the inventory. Prints out possible solutions if it is not.
    returns the number of batches in the inventory."""
    num_batches = 0
    for batch in comment_batches:
        if batch in inventory_batches:
            num_batches += 1
        else:
            print(f"Could not find {batch} in the invenory list. Maybe the inventory has not been updated.")
            print("Or, could be that the wrong settings were used of the sensors have not been recieved.")
            print()
    print(f"Found {num_batches} out of {len(comment_batches)} batches.")
    print()
    return num_batches

def get_upload_serial_numbers(serial_nums, dates, inventory_batches, comment_batches, date):
    """Gets a list of the serial numbers from batches to be commented."""
    upload_serial_nums = []
    for batch in comment_batches:
        if batch in inventory_batches:
            for i in range(len(serial_nums)):
                if dates[i] == date and inventory_batches[i] == batch:
                    upload_serial_nums.append(serial_nums[i])
    return upload_serial_nums

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add comment to component to all ")
    parser.add_argument("--batches", nargs='+', help="Batch numbers of batches to comment. Format: VPXxxxxx")
    parser.add_argument("--date", help="Date the batch was recieved. Format: dd/mm/yyyy")
    parser.add_argument("--message", "-m", dest="message", help="Comment to apply.")
    parser.add_argument("--test", action="store_true", help="Don't write to DB.")
    parser.add_argument("--verbose", action="store_true",
                        help="Print what's being sent and received.")

    args = parser.parse_args()

    inventory_filename = INVENTORY_FILENAME
    serial_nums, dates, inventory_batches = get_inventory_info(inventory_filename)
    num_batches = check_batches(inventory_batches, args.batches)
    
    if num_batches == 0:
        print("Found no matching batches in inventory. Check the inventory file.")
        print("Exiting program")
        sys.exit(1)

    upload_serial_nums = get_upload_serial_numbers(serial_nums, dates, inventory_batches, args.batches, args.date)

    if len(upload_serial_nums) == 0:
        print("No valid serial numbers found. Check the date input.")
        print("Exiting program")
        sys.exit(1)
    
    print(f"Found {len(upload_serial_nums)} sensors to comment on.")
    print("Opening connection to DB...")

    if args.verbose:
         dbAccess.verbose = True

    if os.getenv("ITK_DB_AUTH"):
         dbAccess.token = os.getenv("ITK_DB_AUTH")

    for serial_num in upload_serial_nums:
        print(f"Have code to refer to component {serial_num}.")

        if not args.message:
            print("Don't have a message. Need a message to comment.")
            sys.exit(1)

        print("Add comment to component:")
        print(f"    Component code: {serial_num}")
        print(f"    Message: {args.message}")
        print()
    
    #Quit program here if just testing
    if args.test:
         sys.exit(1)

    for serial_num in upload_serial_nums:
        try:
            result = dbAccess.doSomething("createComponentComment",{"component": serial_num,"comments": [args.message]})
            #print(result)
            print(f"Uploaded comment for {serial_num}")
        except:
            if args.verbose:
                print("Request failed:")
                import traceback
                traceback.print_exc()
            else:
             print("Request failed, use --verbose flag for more information")


