#Import the dependencies 
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify 

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
print(most_recent_date)

most_recent_date = dt.date(2017, 8, 23)
one_year_from_last = most_recent_date - dt.timedelta(days=365)
print(one_year_from_last)
session.close()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all avalible api routes."""
    return(
        f"Welcome! Here are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs-active<br/>"
        f"/api/v1.0/tobs-one-year<br/>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end><br/>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #Query to return last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_from_last).all()
    session.close()
    
    #Returns json with the date as the key and the value as the precipitation
    one_year_precipitation = []
    for date, prcp in precipitation_data:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        one_year_precipitation.append(precipitation_dict)
    
    return jsonify(one_year_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Returns jsonified data of all of the stations in the database (3 points)
    station_results = session.query(Station.station, Station.name, Station.langitude,
                                    Station.longitude, Station.elevation).all()
    session.close()
    # Convert list of tuples into normal list
    station_list = list(np.ravel(station_results))
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs-active")
def active_station():
# Create our session (link) from Python to the DB
    session = Session(engine)
#Query to return data for most active station
    active_station = session.query(Measurement.date, Measurement.tobs).\
        filter_by(station = "USC00519281").all
    session.close()
# Convert list of tuples into normal list
    active_list = list(np.ravel(active_station))
    
    return jsonify(active_list)

@app.route("/api/v1.0/tobs-one-year")
def one_year_tobs():
 # Create our session (link) from Python to the DB
    session = Session(engine)
#Query to return data for most active station
    one_year = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_from_last).all()
    session.close()
    # Convert list of tuples into normal list
    one_year_list = list(np.ravel(one_year))
    
    return jsonify(one_year_list)

@app.route("/api/v1.0/<start>")
def start_min_max(start):
     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the date greater than or equal to start
    sel = [func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs)
           ]
    start_stats = session.query(*sel).\
    filter(Measurement.date >= start).group_by(Measurement.date).all()
    session.close()
    
   
    start_list = [
        {"Min Temp": start_stats[0][0]},
        {"Max Temp": start_stats[0][1]},
        {"Av Temp": start_stats[0][2]}
         ]
    if start <= '2017-08-23':
        return jsonify(start_list)
    else:
        return jsonify("'Error: Date out of Range, enter date prior to 2017-08-23'")
    

@app.route("/api/v1.0/<start>/<end><br/>")
def start_min_max(start, end):
     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the date greater than or equal to start
    sel = [func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs)
           ]
    start_stats = session.query(*sel).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).\
        group_by(Measurement.date).all()
    session.close()
    
   
    start_end_list = [
        {"Min Temp": start_stats[0][0]},
        {"Max Temp": start_stats[0][1]},
        {"Av Temp": start_stats[0][2]}
         ]
    if (start <= '2017-08-23') and (end >= '2010-01-01'):
        return jsonify(start_end_list)
    else:
        return jsonify("'Error: Dates out of Range, enter dates between 2010-01-01 and 2017-08-23'")
    

if __name__ == '__main__':
    app.run(debug=True)

