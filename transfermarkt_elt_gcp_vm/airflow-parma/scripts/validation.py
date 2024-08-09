import sys
import datetime

def validate_input(date_input: str) -> None:
  """
  Validates that the input is in the correct date format (YYYYMMDD).

  :param date_input: The date input passed as a string.
  :raises ValueError: If the date_input is not in the correct format.
  """
  try:
    datetime.datetime.strptime(date_input, '%Y%m%d')
  except ValueError:
    print("Input parameter should be YYYYMMDD")
    sys.exit(1)