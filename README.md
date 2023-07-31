# sns-query-orchestrator
**Description:**

The provided Python script is a tool for interacting with AWS SNS (Simple Notification Service) to query and analyze various resources such as topics and subscriptions. The script uses the Boto3 library, which is the AWS SDK for Python, to communicate with AWS services.

**Features:**

1.  List SNS Topics Without Subscriptions: The script identifies SNS topics that do not have any subscriptions and displays relevant information, including topic ARN, TerraformManaged tag, and Product tag ( (modifiable as per user needs)).
2.  List Subscribers Listening to Multiple Topics: The script finds subscribers who are listening to multiple SNS topics. It prints the subscribers' endpoint along with the topics they are subscribed to.
3.  List Topics with Multiple Subscribers: The script identifies SNS topics that have multiple subscribers and displays the topic ARN and associated subscriber endpoints.
4.  Group Subscriptions by Criteria: The script categorizes subscriptions into two groups based on their endpoint format: phone numbers and email addresses.

**Prerequisites:**

-   Python 3.x installed on the machine.
-   Boto3 library installed (**pip install boto3**).

**Usage:**

1.  Before running the script, make sure that AWS credentials are properly configured on the machine where the script is executed.
2.  Uncomment the sections in the **__main__** function to execute the desired queries.
3.  Update the **output_file_txt** and **output_file_csv** variables in the **__main__** function to specify the file paths for saving the results in text and CSV formats.
4.  Execute the script by running **python script_name.py** in the command-line interface.

**Output:**

The script will generate two output files:

-   **sns3_output.txt**: Contains the console output of the script, including the queried data and analysis results.
-   **sns3_output.csv**: Contains the data of SNS topics without subscriptions in CSV format, including topic ARN, TerraformManaged tag, and Product tag ( (modifiable as per user needs)).

**Important Notes:**

-   It is crucial to ensure that the AWS credentials have the appropriate permissions to interact with SNS resources. Inadequate permissions may lead to errors or incomplete results.
-   The script should be thoroughly tested in a non-production environment before using it in a production setting.
-   For more complex use cases or specific requirements, the script may require further customization.
