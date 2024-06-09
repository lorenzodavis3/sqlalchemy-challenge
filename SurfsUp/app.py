# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import numpy as np
import datetime as dt


#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

def get_session():
    return Session(engine)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
       f"<h1>Welcome to the Hawaii Climate API!</h1>"
        f"<h2>Available Routes:</h2>"
        f"<ul>"
        f"<li><strong>Precipitation Data:</strong> <code>/api/v1.0/precipitation</code><br/>"
        f"Returns precipitation data for the last year from the database.</li>"

        f"<li><strong>Stations List:</strong> <code>/api/v1.0/stations</code><br/>"
        f"Returns a list of weather observation stations.</li>"

        f"<li><strong>Temperature Observations:</strong> <code>/api/v1.0/tobs</code><br/>"
        f"Returns temperature observations for the most active station for the last year.</li>"

        f"<li><strong>Temperature Range from Start Date:</strong> <code>/api/v1.0/&lt;start&gt;</code><br/>"
        f"Returns the minimum, average, and maximum temperatures from the start date to the end of the dataset. <br/>"
        f"Example: <code>/api/v1.0/2017-01-01</code></li>"

        f"<li><strong>Temperature Range between Dates:</strong> <code>/api/v1.0/&lt;start&gt;/&lt;end&gt;</code><br/>"
        f"Returns the minimum, average, and maximum temperatures between the start and end dates. <br/>"
        f"Example: <code>/api/v1.0/2017-01-01/2017-01-10</code></li>"
        f"</ul>"

        f"<p>Please use 'YYYY-MM-DD' format for all date inputs.</p>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = get_session()
    try:
        one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
        results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value
        precipitation_dict = {date: prcp for date, prcp in results}
        return jsonify(precipitation_dict)
    finally:
        session.close()

@app.route("/api/v1.0/stations")
def stations():
    session = get_session()
    try:
        stations_data = session.query(Station.station).all()
        stations_list = [station[0] for station in stations_data]
        return jsonify(stations_list)
    finally:
        session.close()

@app.route("/api/v1.0/tobs")
def tobs():
    session = get_session()
    
    # Query the dates and temperature observations of the most active station for the last year of data
    try:
        one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
        results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= one_year_ago).all()

    # Convert list of tuples into normal list
        tobs_list = {date: tobs for date, tobs in results}
        return jsonify(tobs_list)
    finally:
        session.close()

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def range_temp(start, end=None):
    session = get_session()
    
    # Query the min, avg, and max temperatures for dates between the start and end date inclusive
    try:
        if end:
            results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).all()
        else:
            results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    # Convert list of tuples into normal list
        temp_list = list(np.ravel(results))
        return jsonify(temp_list)
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True)