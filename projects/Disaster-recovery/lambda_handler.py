# lambda_handler.py
from lambda_restore import main as restore_main

def lambda_handler(event, context):
    # adapt the old script to a callable structure
    return restore_main(event, context)

