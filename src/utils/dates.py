from datetime import date

from fiscalyear import FiscalDate, FiscalQuarter

"""
A series of functions to help determine if the fy/fq will provide data.
Federal Gov FY is October 1 of one calendar year through September 30 of the next.
There is a delay when data is published to the USA spending API.
This can be used to guide the LLM to adjust its dates.
"""


def get_cur_fy_fq():
    f = FiscalDate.today()
    return f.fiscal_year, f.fiscal_quarter


# Often, there is a lag when data is published
# For example, 45 days after the most recent quarter closed
# This function will return the most recent FY/FQ that has data
def latest_fy_fq_with_data(lag=45):
    fq = FiscalQuarter.current()
    start_date = date(fq.start.year, fq.start.month, fq.start.day)
    time_diff = date.today() - start_date
    if time_diff.days < lag:
        fq = fq.prev_fiscal_quarter.prev_fiscal_quarter
        return fq.fiscal_year, fq.fiscal_quarter

    return fq.fiscal_year, fq.fiscal_quarter


# Helper function to return T/F if there is a more recent fy fq
def is_outdated_fy_fq(lower_fy, lower_fq, upper_fy, upper_fq):
    try:
        lower_fy = int(lower_fy)
        lower_fq = int(lower_fq)
        upper_fy = int(upper_fy)
        upper_fq = int(upper_fq)
        lower = FiscalQuarter(lower_fy, lower_fq)
        upper = FiscalQuarter(upper_fy, upper_fq)
        return lower < upper
    except TypeError as e:
        print(f"Unable to cast fy/fq to int {e=}")
    except Exception as e:
        print(f"Unexpected error occurred in is_outdated_fy_fq {e=} and {type(e)=}")

    return None


# Many of these functions depend on quarter
# Sometimes a period can be provided
# Find out which period the quarter is in
def period_to_quarter(period):
    if period > 0 and period <= 3:
        return 1
    if period > 3 and period <= 6:
        return 2
    if period > 6 and period <= 9:
        return 3
    if period > 9 and period <= 12:
        return 4
    return None
