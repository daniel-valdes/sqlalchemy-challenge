# import dependencies we need to query a sqlite databse with sqlalchemy and return output to flask as json's

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# create enginge to link to sqlite file/database
engine = create_engine("sqlite:////Users/danvaldes/Desktop/bootcamp/sqlalchemy-challenge/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables into classes
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# FLASK APP INITIALIZED
app = Flask(__name__)

@app.route("/")
def Home():
    return(
        f"<h3>Available Routes:<hr></h3>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/start_date</br>"
        f"/api/v1.0/start_date/end_date</br>"
        )


@app.route("/api/v1.0/precipitation")
def precipitation():
        
        # INITIATE A SESSION, CREATE QUERY, CLOSE SESSION
        session = Session(engine)

        year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

        results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).all()

        session.close()

        prcp_dict = dict(results)

        return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():

        # INITIATE A SESSION, CREATE QUERY TO RETURN A LIST OF STATIONS, CLOSE SESSION
        session = Session(engine)

        sel = [Measurement.station, Station.name, func.count(Measurement.station)]

        # SESSION.QUERY METHOD RETURNS A LIST OF TUPLES
        results = session.query(*sel).filter(Measurement.station == Station.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

        session.close()

        # LIST(NP.RAVLE(LIST_NAME)) UNRAVELS THE LIST
        # station_list = list(np.ravel(results))

        return jsonify(results)


@app.route("/api/v1.0/tobs")
def tobs():

        # INITIATE A SESSION, CREATE QUERY, CLOSE SESSION
        session = Session(engine)

        year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

        datapoints = session.query(Measurement.tobs).\
        filter(Measurement.date >= year_ago).\
        filter(Measurement.station == 'USC00519281').all()

        session.close()

        return jsonify(datapoints)


# DEFINE THE CALC_TEMPS FUNCTION
def calc_temps(start_date, end_date):

                my_data_returned= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
                return my_data_returned


@app.route("/api/v1.0/<start>")
def start(start):

        session = Session(engine)
        date_to_pass=start

        # INLINE FUNCTION TO CALCULATE MIN, AVG, AND MAX. CAN'T CALL CALC_TEMPS BECAUSE IT REQUIRES TWO PARAMS
        last_date = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date==date_to_pass).all()

        my_date=list(np.ravel(last_date))
        session.close()

        return jsonify(my_date)



@app.route("/api/v1.0/<start_date>/<end_date>") 
def start_end(start_date=None, end_date=None):
        
        temps = calc_temps(start_date, end_date)
        return jsonify(temps)



if __name__ == "__main__":
    app.run(debug=True)
