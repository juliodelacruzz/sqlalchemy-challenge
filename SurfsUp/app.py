# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
# creating engine 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

#landingpage/homepage

@app.route("/")

def welcome():
    return (
        #listing api endpoints
        f"Welcome to My Climate App!<br/>"
        f"Here are the avaliable enpoints:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/><br/>"
    )

# Precipitation 
@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # query for rain data based on most recent year and exactly 1 year ago 
    rain_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()

    #we must close the session after each api endpoint to ensure good database connections
    #saves resources and provides session independence

    session.close()


    # Convert the query results to a dictionary using date as the key and prcp as the value
    #then retun data jsonified
    rain_dict = {date: prcp for date, prcp in rain_data}

    return jsonify(rain_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)
    
    # getting station data
    station_data = session.query(Station.station).all()

    session.close()

    # Convert the query results to a list
    # makes it easier to handle and use the data, especially when you need to return it in a JSON format, numpy's ravel() function turns it into a more JSON-friendly format.
    stations_list = list(np.ravel(station_data))

    return jsonify(stations_list)

# Temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    
    # getting last year
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # we know the most active is USC00519281, and we can align our query from there
    most_active_data = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= last_year).all()

    session.close()
    tobs_list = list(np.ravel(most_active_data))
    return jsonify(tobs_list)

# Temperature statistics route
@app.route("/api/v1.0/<start_date>")
def start(start_date):
    # TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    session = Session(engine) 

    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

    # list of dictionaries for jsonify
    temps = list(np.ravel(temps))

    return jsonify(temps)

# Temperature statistics route for a specified start date and end date
@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_route(start_date, end_date):

    session = Session(engine)

    two_temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    
    session.close()

    two_temps = list(np.ravel(two_temp_stats))

    return jsonify(two_temps)

if __name__ == "__main__":
    app.run(debug=True)

