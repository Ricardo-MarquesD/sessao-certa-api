from datetime import datetime, timedelta

class TimeManipulation:
    @staticmethod
    def time_diference(date: datetime, date_sub: datetime | None = None)->timedelta:
        if date_sub is None:
            date_sub = datetime.now()
        if not isinstance(date, datetime):
            raise ValueError("date must be a datetime")
        if not isinstance(date_sub, datetime):
            raise ValueError("date_sub must be a datetime")
        
        return date - date_sub
    
if __name__ == "__main__":
    res = TimeManipulation.time_diference(datetime(2025,12,31,15,30,45))
    print(type(res))
    print(res)