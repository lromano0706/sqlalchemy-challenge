import numpy as np
import datetime as dt
import pandas as pd
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
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
Climate_app = Flask(__name__)

@Climate_app.route("/")
def Home_Page():
    """List all routes that are available."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt; where start is a date in YYYY-MM-DD format <br>" 
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; where start and end are dates in YYYY-MM-DD format"
        
    )

@Climate_app.route("/api/v1.0/precipitation")
def Precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all Date & Precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()    
    
    session.close()
    
    # Create a dictionary from the row data and append to a list of Dates & Precipitation
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@Climate_app.route("/api/v1.0/stations")
def Stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all stations
    results = session.query(Station.station).all() 
    
    session.close()
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@Climate_app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Query all tobs
    results = session.query(Measurement.tobs).filter(Measurement.station == "USC00519281").\
    filter(Measurement.date >= query_date).all() 
    
    session.close()
    
    most_active = list(np.ravel(results))
    return jsonify(most_active)

@Climate_app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query given start and calculating min avg max for all dates greater than and equal to th start date.
    start_date = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).group_by(Measurement.date).all()
    # Convert list of tuples into normal list
    start_date_list = list(np.ravel(start_date))
    return jsonify(start_date_list)

@Climate_app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query given start and calculating min avg max for all dates greater than and equal to th start date and end date
    start_end_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    
    session.close()
        
    return jsonify(start_end_day)    

if __name__ == '__main__':
    Climate_app.run(debug=True)
