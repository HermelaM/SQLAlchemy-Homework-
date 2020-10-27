import pandas as pd
import numpy as np
import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup

app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    return (
        
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/temp/start/end'>api/v1.0/temp/start/end</a>"   
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    session.close()
    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
        session = Session(engine)
        # Return a JSON List of Stations From the Dataset
        stations = session.query(Station.station, Station.name).all()

        session.close()
        # Convert List of Tuples Into Normal List
        station_list = list(stations)
        # Return JSON List of Stations from the Dataset
        return jsonify(station_list)
    


@app.route("/api/v1.0/tobs")
def temp_monthly():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return the temperature observations (tobs) for previous year."""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    tobs = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00514830').\
        filter(Measurement.date >= prev_year).all()

    session.close()
    #  Convert List of Tuples Into Normal List
    tobs_df = list(np.ravel(tobs))

    # Return the result
    return jsonify(tobs_df)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)
    session.close()
    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)
