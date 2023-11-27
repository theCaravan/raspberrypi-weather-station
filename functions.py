"""Define the functions used in this project"""
import os
import time
import json
import warnings
import traceback
import requests
import slack_sdk
import xmltodict
from unicornhatmini import UnicornHATMini
from constants import *

# Initialize Unicorn Hat Mini
unicornhatmini = UnicornHATMini()


def api_call_to_json(method: str, name: str, url: str, api_calls: int, authentication = None, headers = None,
                     params = None,
                     body = None, mock_run = False) -> [dict, int]:
    """Runs an API call and returns the result in JSON. If mock_run = True, print the result here instead."""
    __version__ = "4.2"

    input_arguments = {
        "method"   : method,
        "name"     : name,
        "url"      : url,
        "api_calls": api_calls,
        "headers"  : headers,
        "params"   : params,
        "body"     : body,
        "mock_run" : mock_run,
        }

    # Return a dictionary we will add onto for the full output.
    return_dict = {
        "input_arguments": input_arguments,
        }

    if not body:
        body = {}
    else:
        body = json.dumps(body)

    try:
        if mock_run:
            print("--- api_call_to_json: This would have been sent ---")
            print("input_arguments = {}".format(input_arguments))
            print("--- api_call_to_json: End ---")

            return_dict["result"] = "success"
            return_dict["status_code"] = 204
            return_dict["api_calls"] = api_calls
            return_dict["output"] = {}
            return return_dict, api_calls

        if method == "GET":
            response = requests.get(url = url,
                                    auth = authentication,
                                    headers = headers,
                                    params = params,
                                    data = body)
            api_calls += 1

        elif method == "POST":
            response = requests.post(url = url,
                                     auth = authentication,
                                     headers = headers,
                                     params = params,
                                     data = body)
            api_calls += 1

        elif method == "PUT":
            response = requests.put(url = url,
                                    auth = authentication,
                                    headers = headers,
                                    params = params,
                                    data = body)
            api_calls += 1

        elif method == "DELETE":
            response = requests.delete(url = url,
                                       auth = authentication,
                                       headers = headers,
                                       params = params,
                                       data = body)
            api_calls += 1

        else:
            return_dict["result"] = "error"
            return_dict["error"] = "invalid_or_unsupported_method"
            return_dict["api_calls"] = api_calls
            return return_dict, api_calls

        return_dict["status_code"] = response.status_code

        # 204 – No Content
        # Request succeeded, but nothing returned that would be worth a JSON conversion.
        if return_dict["status_code"] == 204:
            return_dict["result"] = "success"
            return_dict["wasXML"] = False
            return_dict["output"] = response.text
            return_dict["api_calls"] = api_calls
            return return_dict, api_calls

        # 429 – Too Many Requests
        # if a 429, lets call this again after sleeping for the amount specified in the request.
        if return_dict["status_code"] == 429:
            sleep_seconds = 5

            if "retry-after" in response.headers.keys():
                sleep_seconds = float(response.headers["retry-after"])

            if mock_run:
                print("Got a 429 in {} '{}' for '{}'. Will sleep for {} seconds and then try again."
                      .format(method, url, name, sleep_seconds))

            time.sleep(sleep_seconds)

            # One of the few times I ever use recursion, a function invoking itself.
            # Theoretically if we keep getting 429s this can run forever.
            return api_call_to_json(method, name, url, api_calls, authentication, headers, body, mock_run)

        if return_dict["status_code"] >= 400:
            return_dict["result"] = "error"
            return_dict["error"] = "http_error_returned"
            return_dict["api_calls"] = api_calls
            return_dict["response"] = response
            try:
                return_dict["response.content"] = json.loads(response.content)
            except json.decoder.JSONDecodeError:
                return_dict["response.content"] = str(response.content)

            return return_dict, api_calls

        try:
            # If the result is XML, convert it to JSON
            if "<?xml version" in response.text:
                # Remove everything before the first <?xml version>"
                return_dict["result"] = "success"
                return_dict["wasXML"] = True
                return_dict["api_calls"] = api_calls
                return_dict["output"] = xmltodict.parse(response.text[response.text.find("<?xml version"):])
                return return_dict, api_calls

            else:
                return_dict["result"] = "success"
                return_dict["wasXML"] = False
                return_dict["api_calls"] = api_calls
                return_dict["output"] = json.loads(response.text)
                return return_dict, api_calls

        except Exception as e:
            print(repr(e))
            traceback.print_exc()
            return_dict["result"] = "error"
            return_dict["error"] = "json_parse_error"
            return_dict["api_calls"] = api_calls
            return_dict["response"] = response
            return return_dict, api_calls

    except TimeoutError:
        print("api_call_to_json encountered a timeout error at {} ({})".format(name, url))
        return_dict["result"] = "error"
        return_dict["error"] = "timeout_decorator_triggered"
        return_dict["api_calls"] = api_calls
        return return_dict, api_calls

    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        return_dict["result"] = "error"
        return_dict["error"] = "catchall_failure"
        return_dict["api_calls"] = api_calls
        return return_dict, api_calls


def post_to_slack(slack_channel: str, post_text: str,
                  slack_api_key: str, api_calls: int, mock_run: bool, post_image = None) -> [dict, int]:
    """Post text or image to Slack. If mock_run = True, print the text or image here instead."""
    __version__ = "3.0"

    input_arguments = {
        "slack_channel": slack_channel,
        "post_text"    : post_text,
        "slack_api_key": "[REDACTED]",
        "api_calls"    : api_calls,
        "mock_run"     : mock_run,
        "post_image"   : post_image,
        }

    validate_environment_variables("post_to_slack",
                                   [
                                       slack_api_key,
                                       ])

    try:
        if post_image:
            if mock_run:
                print("This would have posted to {}: ---".format(slack_channel))
                print(post_text)
                print("[Image goes here. It's been saved locally]")
                print("--- ---")
                return {
                    "result"         : "success",
                    "api_calls"      : api_calls,
                    "input_arguments": input_arguments
                    }, api_calls

            # client.files_upload() has a warning
            # UserWarning: client.files_upload() may cause some issues like timeouts for relatively large files.
            # Our latest recommendation is to use client.files_upload_v2(), mostly compatible and much stabler,
            # instead.
            #
            # I couldn't get client.files_upload_v2() to work, so instead we suppress the warnings for it.

            client = slack_sdk.WebClient(os.environ[slack_api_key])

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                response = client.files_upload(channels = [slack_channel],
                                               initial_comment = post_text,
                                               file = post_image)
                api_calls += 1

            return {
                "result"         : "success",
                "output"         : response,
                "api_calls"      : api_calls,
                "input_arguments": input_arguments,
                }, api_calls

        else:
            if mock_run:
                print("--- post_to_slack: This would have posted to Slack Channel '{}' ---".format(slack_channel))
                print(post_text)
                print("--- post_to_slack: End ---")
                return {
                    "result"         : "success",
                    "api_calls"      : api_calls,
                    "input_arguments": input_arguments
                    }, api_calls

            client = slack_sdk.WebClient(os.environ[slack_api_key])
            response = client.chat_postMessage(channel = slack_channel,
                                               text = post_text)
            api_calls += 1

            return {
                "result"         : "success",
                "output"         : response,
                "api_calls"      : api_calls,
                "input_arguments": input_arguments,
                }, api_calls

    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        return {
            "result"         : "error",
            "error"          : "catchall_failure",
            "api_calls"      : api_calls,
            "input_arguments": input_arguments,
            }, api_calls


def validate_environment_variables(module: str, required_environment_variables_list: list) -> None:
    """Verify the needed environment variables are active, otherwise exist with error."""
    __version__ = "1.0"

    if not required_environment_variables_list:
        return

    missing_var = False
    for environment_var in required_environment_variables_list:
        if environment_var not in os.environ.keys():
            print("Required environment variable {} for {} is not set".format(environment_var, module))
            missing_var = True
    if missing_var:
        exit(1)


def clear_section(start_x, end_x, start_y, end_y):
    """Clear a section of pixels, such as when changing the number or an entire line for a new hour."""
    this_x = start_x

    if start_x > end_x:
        print("Error, cannot clear section as start_x: {} is greater than end_x: {}".format(start_x, end_x))

    if start_y > end_y:
        print("Error, cannot clear section as start_y: {} is greater than end_y: {}".format(start_y, end_y))

    while this_x <= end_x:
        this_y = start_y
        while this_y <= end_y:
            unicornhatmini.set_pixel(this_x, this_y, 0, 0, 0)
            this_y += 1
        this_x += 1

    time.sleep(TIME_DELAY)
    unicornhatmini.show()


def display_number(number, x_offset, y_offset, clear = False, rgb = None, test = False):
    """Display a single number"""
    if rgb is None:
        rgb = COLORS["white"]

    if clear or test:
        unicornhatmini.clear()

    red = rgb[0]
    green = rgb[1]
    blue = rgb[2]

    for pixel in NUMBERS_TO_DRAW[number]:
        unicornhatmini.set_pixel(pixel[0] + x_offset, pixel[1] + y_offset, red, green, blue)

        # Show the same number 6 times to ensure the display is working on the test mode.
        if test:
            unicornhatmini.set_pixel(pixel[0] + x_offset + 6, pixel[1] + y_offset, red, green, blue)
            unicornhatmini.set_pixel(pixel[0] + x_offset - 5, pixel[1] + y_offset, red, green, blue)
            unicornhatmini.set_pixel(pixel[0] + x_offset, pixel[1] + y_offset - 4, red, green, blue)
            unicornhatmini.set_pixel(pixel[0] + x_offset + 6, pixel[1] + y_offset - 4, red, green, blue)
            unicornhatmini.set_pixel(pixel[0] + x_offset - 5, pixel[1] + y_offset - 4, red, green, blue)

        unicornhatmini.show()
        time.sleep(TIME_DELAY)


def test_numbers():
    """Initial run of the clock to show you the numbers and to verify it all works."""
    current_number = 9
    while current_number >= 0:
        display_number(current_number, 0, 0, test = True)
        time.sleep(TIME_DELAY * 2)
        current_number -= 1
    unicornhatmini.clear()
