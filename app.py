import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
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
Station=Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
app.config['JSON_SORT_KEYS']= False


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<strong>Available Routes:</strong><br/>"
        f"<br/>Precipitationin all stations :      /api/v1.0/precipitation<br/>"
        f"<br/>List of Stations:                   /api/v1.0/stations<br/>"
        f"<br/>Temperature observations for most active station:           /api/v1.0/tobs<br/>"
        f"<br/>TMIN,TAVG,TMAX for all dates greater start date 'yyyy-mm-dd':  /api/v1.0/start'yyyy-mm-dd'<br/>"
        f"For Example: /api/v1.0/2012-05-21'<br/>"

        f"<br/>TMIN,TAVG,TMAX for dates between the start and end date:   /api/v1.0/start/end <br/>"              
        f"For Example: /api/v1.0/2012-05-21/2012-05-29<br/>"

    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    #Note: Because the date is not unique we return the station ID too
    session = Session(engine)
    results = session.query(Measurement.station,Measurement.date,Measurement.prcp).all()
    session.close()

    # Convert list of tuples into normal list
    PRCP = []
    for station,date,prcp in results:
        Temp_dict={}
        Temp_dict["station"] = station
        Temp_dict["date"] = date
        Temp_dict["prcp"] = prcp

        PRCP.append(Temp_dict)

    return jsonify(PRCP)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    ST = list(np.ravel(results))
    
    return jsonify(ST)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    Data_date=session.query(Measurement.date,Measurement.station,Measurement.tobs)
    #Finding the start day the for mian query
    Max_date=dt.datetime.strptime(max(Data_date)[0],'%Y-%m-%d')
    Last_year=Max_date-dt.timedelta(days=365)
    Last_year_date=Last_year.strftime('%Y-%m-%d')
    #Finding the most active station id for main query       
    Measurement_data2 = session.query(Measurement.station,func.count(Measurement.tobs))\
                                    .group_by(Measurement.station).all()
    MAX_row=0
    MAX_id=""
    for i in range (0,len(Measurement_data2)-1):
        if Measurement_data2[i][1] > MAX_row :
            MAX_row=Measurement_data2[i][1]
            MAX_id=Measurement_data2[i][0]
    #Generating the final query : Query the dates and temperature observations of the most active station for the last year of data.
    results=session.query(Measurement.station,Measurement.date,Measurement.tobs)\
                        .filter(Measurement.date >= Last_year_date)\
                        .filter(Measurement.station == MAX_id).all()
                            
    session.close()

    # Convert list of tuples into normal list
    #TOBS = list(np.ravel(results))
    TOBS= []
    for station,date,tobs in results:
        temp_dict = {}
        temp_dict["Station"] = station
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        TOBS.append(temp_dict)
    



    return jsonify(TOBS)

    
    
    
@app.route("/api/v1.0/<start>")
def Start_day(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Generating the final query: TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    results=session.query(Measurement.station,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.station).all()
    session.close()

    TOBS_ST= []
    for station,tmin,tmax,tavg in results:
        temp_dict = {}
        temp_dict["Station"] = station
        temp_dict["Min"] = tmin
        temp_dict["Max"] = tmax
        temp_dict["Avg"] = tavg
        TOBS_ST.append(temp_dict)
    
    return jsonify(TOBS_ST)
    
    
@app.route("/api/v1.0/<start>/<end>")
def Start_End_day(start,end):
        # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Generating the final query: TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

    results=session.query(Measurement.station,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.station).all()
    session.close()

 
    TOBS_ST= []
    for station,tmin,tmax,tavg in results:
        temp_dict = {}
        temp_dict["Station"] = station
        temp_dict["Min"] = tmin
        temp_dict["Max"] = tmax
        temp_dict["Avg"] = tavg
        TOBS_ST.append(temp_dict)
    
    return jsonify(TOBS_ST)
    
     
    
if __name__ == '__main__':
    app.run(debug=True)
