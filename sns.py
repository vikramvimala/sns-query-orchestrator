import boto3
import sys
import csv
sns = boto3.client('sns', region_name='us-east-1')

# Global variables to store topics and subscriptions data
topics_data = None
subscriptions_data = None
topic_tags_data = {}  # Dictionary to store tags for each topic

def list_resources(client, resource_type, list_function):
    resources = []

    response = list_function()
    while True:
        resources.extend(response[resource_type])

        if 'NextToken' in response:
            response = list_function(NextToken=response['NextToken'])
        else:
            break

    return resources

def fetch_topic_tags(topic_arn):
    if topic_arn not in topic_tags_data:
        topic_tags_data[topic_arn] = sns.list_tags_for_resource(ResourceArn=topic_arn)['Tags']

def get_sns_topics_without_subscriptions():
    topics_without_subscriptions = []

    for topic in topics_data:
        topic_arn = topic['TopicArn']
        subscriptions = [sub['SubscriptionArn'] for sub in subscriptions_data if sub['TopicArn'] == topic_arn]
        if not subscriptions:
            fetch_topic_tags(topic_arn)  # Fetch tags if not already fetched
            topic_tags = topic_tags_data[topic_arn]
            terraform_managed_tag = next((tag['Value'] for tag in topic_tags if tag['Key'] == 'TerraformManaged'), None)
            product_tag = next((tag['Value'] for tag in topic_tags if tag['Key'] == 'Product'), None)
            topics_without_subscriptions.append({
                "TopicArn": topic_arn,
                "TerraformManaged": terraform_managed_tag,
                "Product": product_tag
            })

    return topics_without_subscriptions

def get_subscribers_for_multiple_topics():
    all_subscribers = {}
    total_subscribers = 0

    for sub in subscriptions_data:
        endpoint = sub['Endpoint']
        topic_arn = sub['TopicArn']
        if endpoint not in all_subscribers:
            all_subscribers[endpoint] = []
        all_subscribers[endpoint].append(topic_arn)

    for endpoint, topics in all_subscribers.items():
        if len(topics) > 1:
            total_subscribers += 1
            print(f"Subscriber: {endpoint}")
            print("Topics:")
            for topic_arn in topics:
                print(topic_arn)
            print()

    print(f"Total count of subscriptions with more than 1 topic: {total_subscribers}")

def get_topics_with_multiple_subscribers():
    topics_with_multiple_subscribers = {}

    for topic in topics_data:
        topic_arn = topic['TopicArn']
        subscribers = [sub['Endpoint'] for sub in subscriptions_data if sub['TopicArn'] == topic_arn]
        if len(subscribers) > 1:
            topics_with_multiple_subscribers[topic_arn] = subscribers

    return topics_with_multiple_subscribers

def is_phone_number(endpoint):
    return endpoint.startswith('+')

def group_subscriptions_by_criteria(subscriptions_list):
    subscriptions_by_phone = []
    subscriptions_by_email = []

    for sub in subscriptions_list:
        endpoint = sub['Endpoint']
        topic_arn = sub['TopicArn']

        if is_phone_number(endpoint):
            subscriptions_by_phone.append({"Endpoint": endpoint, "TopicArn": topic_arn})
        elif '@' in endpoint:
            subscriptions_by_email.append({"Endpoint": endpoint, "TopicArn": topic_arn})

    return subscriptions_by_phone, subscriptions_by_email

if __name__ == "__main__":
    output_file_txt = "sns3_output.txt"
    output_file_csv = "sns3_output.csv"
    with open(output_file_txt, "w") as f_txt, open(output_file_csv, "w", newline='') as f_csv:
        sys.stdout = f_txt

        # Fetch topics and subscriptions data
        topics_data = list_resources(sns, 'Topics', sns.list_topics)
        subscriptions_data = list_resources(sns, 'Subscriptions', sns.list_subscriptions)

        # Get SNS topics without subscriptions
        print("===============================================================")
        print("\nSNS Topics without subscriptions:\n")
        print("===============================================================\n")
        topics_without_subs = get_sns_topics_without_subscriptions()
        for topic_info in topics_without_subs:
            topic_arn = topic_info['TopicArn']
            terraform_managed = topic_info['TerraformManaged']
            product = topic_info['Product']
            print(f"Topic: {topic_arn}")
            print(f"TerraformManaged: {terraform_managed}")
            print(f"Product: {product}")
            print()

        print(f"\nTotal number of topics: {len(topics_data)}")
        print(f"Total number of subscriptions: {len(subscriptions_data)}")
        print(f"Total topics without subscriptions: {len(topics_without_subs)}")

        # Write the topics_without_subs data to CSV
        fieldnames = ['Topic', 'TerraformManaged', 'Product']
        csv_writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
        csv_writer.writeheader()
        for topic_info in topics_without_subs:
            csv_writer.writerow({
                'Topic': topic_info['TopicArn'],
                'TerraformManaged': topic_info['TerraformManaged'],
                'Product': topic_info['Product']
            })
        
        # Get subscribers listening to multiple SNS topics
        print("\n===============================================================")
        print("\nSubscribers listening to multiple SNS topics:\n")
        print("===============================================================\n")
        get_subscribers_for_multiple_topics()

        # Get topics with multiple subscribers
        topics_with_multiple_subs = get_topics_with_multiple_subscribers()
        print("\n===============================================================")
        print("\nTopics with multiple subscribers:\n")
        print("===============================================================\n")
        for topic_arn, subscribers in topics_with_multiple_subs.items():
            print(f"Topic ARN: {topic_arn}")
            print("Subscribers:")
            for subscriber in subscribers:
                print(subscriber)
            print()
        print(f"Total count of topics with multiple subscribers: {len(topics_with_multiple_subs)}")

        # Group subscriptions by complete phone numbers starting with '+'
        subscriptions_by_phone, subscriptions_by_email = group_subscriptions_by_criteria(subscriptions_data)
        print("\n===============================================================")
        print("\nSubscriptions with Phone Numbers as Endpoints:\n")
        print("===============================================================\n")
        for sub in subscriptions_by_phone:
            print(f"  Endpoint: {sub['Endpoint']}")
        print()

        # Group subscriptions with '@' in their endpoints
        print("===============================================================")
        print("\nSubscriptions with mail as Endpoints:\n")
        print("===============================================================\n")
        for sub in subscriptions_by_email:
            print(f"  Endpoint: {sub['Endpoint']}")
        print()

    sys.stdout = sys.__stdout__
    print(f"Output saved to '{output_file_txt}' and '{output_file_csv}'.")
