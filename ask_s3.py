#!/usr/bin/env python

"""
Command line tool for listing stuff in an S3 bucket/folder. WIP
"""

import time
import botocore
import boto3


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query an S3 bucket for objects. The --folder option limits the"
                                                 "listing to the stuff inside a given folder or sub-folder and the "
                                                 "--suffix option limits the listing to objects with a given suffix")

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true")

    parser.add_argument("-b", "--bucket", help="The S3 Bucket name", required=True,
                        default='hyrax_regression_tests_data')
    parser.add_argument("-f", "--folder", help="Only show objects in the bucket with this folder name", default='')
    parser.add_argument("-s", "--suffix", help="Only show objects in the bucket/folder with this suffix")

    args = parser.parse_args()

    try:
        start = time.time()

        session = boto3.Session()
        s3 = session.resource('s3')
        bucket = s3.Bucket(args.bucket)

        for bucket_object in bucket.objects.filter(Prefix=args.folder):
            if args.suffix:
                key = bucket_object.key
                if key.endswith(args.suffix):
                    print(f'key: {key}')
            else:
                print(f'key: {bucket_object.key}')

        duration = time.time() - start
        print(f'Request time: {duration:.1f}s') if args.time else ''

    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'LimitExceededException':
            print('API call limit exceeded')
        else:
            raise error


if __name__ == "__main__":
    main()
