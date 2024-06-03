import React from 'react';

const NYCTripModalContent = ({ node }) => {
    const { trip_details } = node;
    const destination = trip_details.destinations[0];
    const accommodation = destination.accommodation;
    const activity = destination.activities[0];

    return (
        <div>
            <div className="header">
                <h1>{trip_details.trip_name}</h1>
                <p>{trip_details.start_date} to {trip_details.end_date}</p>
            </div>
            <div className="content">
                <div className="card">
                    <div className="map" style={{ backgroundImage: `url(${destination.map_image_url})` }}></div>
                    <div className="card-content">
                        <h3>{destination.location}</h3>
                        <p>Arrival: {destination.arrival_date} | Departure: {destination.departure_date}</p>
                    </div>
                </div>
                <div className="card">
                    <img src={accommodation.image_url} alt={accommodation.name} />
                    <div className="card-content">
                        <h3>{accommodation.name}</h3>
                        <p>Address: {accommodation.address}</p>
                        <p>Check-in: {accommodation.check_in} | Check-out: {accommodation.check_out}</p>
                        <p>Total Price: {accommodation.currency} {accommodation.price_total}</p>
                    </div>
                </div>
                <div className="card">
                    <img src={activity.image_url} alt={activity.name} />
                    <div className="card-content">
                        <h3>{activity.name}</h3>
                        <p>Date: {activity.date} | Time: {activity.time}</p>
                        <p>Location: {activity.location}</p>
                        <p>Notes: {activity.notes}</p>
                        <a href={activity.purchase_url} className="activity-button" target="_blank" rel="noopener noreferrer">Buy Tickets</a>
                    </div>
                </div>
            </div>
            <div className="footer">
                <p>{trip_details.notes}</p>
                <p>Number of Adults: {trip_details.number_of_adults} | Number of Children: {trip_details.number_of_children}</p>
            </div>
        </div>
    );
};

export default NYCTripModalContent;
