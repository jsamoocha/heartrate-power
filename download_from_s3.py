import os
import re

import boto3
import requests


def download_from_s3():
    s3_bucket_name = 'heartrate-power-streams'
    s3_base_url = 'https://s3-eu-west-1.amazonaws.com/heartrate-power-streams/{key}'

    s3 = boto3.resource('s3')
    s3_bucket = s3.Bucket(s3_bucket_name)


    for obj in s3_bucket.objects.all():
        match = re.search('^(?P<athlete>.*)/(?P<activity>.*).json$', obj.key)
        athlete = match.group('athlete')
        activity = match.group('activity')

        directory = os.path.join('data', athlete)
        if not os.path.exists(directory):
            os.makedirs(directory)

        r = requests.get(s3_base_url.format(key=obj.key))
        with open(os.path.join(directory, activity + '.json'), "w") as f:
            f.write(r.content.decode('utf-8'))


if __name__ == "__main__":
    download_from_s3()
