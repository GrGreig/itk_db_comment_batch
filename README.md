# Batch level comments for the ITk DB.

Program to add comments to batch wide components in the ITk database for shipping purposes. 

Until itk_pdb is pip installable, this should be saved directly to the 
'production_database_scripts' directory.

This requires the use of requests, and itkdb. Both can be indtalled using:

```
pip install requests, itkdb
```

This module depends on having an up to date inventory CSV file. This can be generated
with the inventory2CSV.py script. This is done in the production_database_scipts folder with the command:

```
python inventory2CSV.py --project S 
                        --componentType SENSOR 
                        --currentLocation <location> 
                        --properties -1 
                        --outfile <output_file_name>
                        --write serialNumber
 ```
Where <output_file_name> is a choosen .csv file. For simplicity I use 'sensor_inventory.csv'. If you choose a different name, the following line
must be changed in the script:
  
```
  INVENTORY_FILENAME = 'sensor_inventory.csv'
```

Change this to whatever <output_file_name> you choose. 
                        
To run this command, ensure you are in the 'production_databse_scripts' directory and run the following command:
  
```
  python add_batch_comments.py --batches <list_of_batch_numbers> --date <date_recieved> --message <string_message_variable> 
  
```

The ```<list_of_batch_numbers>``` parameter is a list of sensor batch numbers of the form VPXxxxxx where the x's form the distinct batch number and are separated by commas.
  
The ```<date_recieved>``` can be found in the inventory file and has the format dd/mm/yyyy
  
The ```message``` must be a string surrounded by quotations. 
  
The example:
 
```
python add_batch_comments.py --batches VPX34149, VPX34148 --date 16/07/2020  --message "test comment"   
```
Would add the comment 'test comment' to all sensors from the batches VPX34149 and VPX34148 that arrived on 16/072020. 
  
Note, one can add '''--test''' to prevent the comment from being uploaded as a test to make sure everything is correct.
  
ex.)

```
python add_batch_comments.py --batches VPX34149, VPX34148 --date 16/07/2020  --message "test comment" --test 
```
