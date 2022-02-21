# Real State Tracker Backend

![](https://i.gifer.com/XkWR.gif)

## Introduction 


This project focuses on tracking users based on longitude and latitude, 
their displacement is determined taking into account the location and the time
when the request it is received by the backend.



The tracking processor only receives the location through an 
endpoint and through a celery task and does all the data.



I used redis to save the current location and paths, because I didn't want to
write them to a field in the database that was going to be constantly 
changing, so I left the location in memory and only used the database for 
these particular tasks.

 - Creating speed and route reports
 - Creating and updating visits
 - Search for properties near a user's location to start a visit automatically


## Things I use Redis on
 - To write and consult the parameters of speed limit and distance recording
 - To save and update the user's location
 - To create the routes and store the data related to distance, time and speed

**Here is the evidence**

I'm using **Medis** as a **Redis GUI**.

![](https://i.imgur.com/GrFnJOX.png)

![](https://i.imgur.com/oPzQTZ9.png)

![](https://i.imgur.com/yG3WHA0.png)

**Libraries that I use for this project**
  - Django==3.2  
  - celery==5.2.3  
  - django-celery-results==2.2.0  
  - django-environ==0.8.1
  - djangorestframework==3.13.1  
  - uWSGI==2.0.20  
  - dj-static==0.0.6
  - drf-extra-fields==3.2.1  
  - drf-yasg==1.20.0  
  - django-json-widget==1.1.1  
  - django-leaflet==0.28.2  
  - redis==4.1.4  
  - psycopg2==2.9.3  
  - django-lifecycle==0.9.6  
  - django-cors-headers==3.11.0  
  - geopy==1.20.0  
  - postgis==1.0.4  
  - djangorestframework-gis==0.18

Instructions to run the project locally

**Create the environment variables**

    cp env_tempate .env

**Build the Docker image**

    docker-compose build

**Up the Docker containers**

    docker-compose up

**Give execution permissions to setup.sh**

    chmod +x setup.sh

**Run setup.sh**

    ./setup.sh

**If you see these messages everything worked fine**

![](https://i.imgur.com/lD6KQEZ.png)

This file is in charge of the following tasks:

- Load the static files of the libraries and the admin
- Create a superuser that has access to the admin
- Create a CompanyUser
- Create 3 Properties in Bogotá Colombia, with address and location

Once configured you can go to the admin and the root of the api

Api: [http://localhost:4500/](http://localhost:4500/)

Admin: 
[http://localhost:4500/admin](http://localhost:4500/admin/)

Admin credentials

    username: admin
    password: 123

## API Description

![enter image description here](https://i.imgur.com/Zs8IStL.png)

![](https://i.imgur.com/TbASEqo.png)

## Api Description

The api has 4 endpoints

- Login
    - http://localhost:4500/auth/users/login/
- Location **(requires auth)**
    - http://localhost:4500/auth/users/location/
- Routes
    - http://localhost:4500/auth/users/{uuid}/routes/
- Visits
    - http://localhost:4500/auth/users/{uuid}/visits/


### Login Description
To log in with a non-administrator user we must use the following request body

[POST]

http://localhost:4500/auth/users/login

    {"username": "test","password": "123"}

I'll use postman for this example

![](https://i.imgur.com/i76bEyt.png)

My response will be 

![](https://i.imgur.com/LKxjJ4w.png)

I'll save the token in my postman environment to get the token when i want

![](https://i.imgur.com/dxofDSo.png)

### Location Description
In this endpoint all the magic of the business happens, the mobile application only has to send the authentication token in the headers and the location whenever it changes, the backend will do the rest by itself

[POST]

http://localhost:4500/auth/users/location/

I'll use postman again for this example and i'll try sending these locations

But we have to setup the headers just like this to authenticate the user in each Http request

![](https://i.imgur.com/QC5Ab42.png)

Now, we are ready to send requests

![](https://i.imgur.com/pHZvkwk.png)

A successful response will look like this

![](https://i.imgur.com/5y3IGpQ.png)

Point 1

    {"latitude": 4.769813, "longitude": -74.027205}

Point 2

    {"latitude": 4.769909, "longitude": -74.030969}

Point 3

    {"latitude": 4.769433, "longitude": -74.031006}

Point 4

    {"latitude": 4.769902, "longitude": -74.032555}

Point 5

    {"latitude": 4.768804, "longitude": -74.032576}

This is the last location (point 5)
![](https://i.imgur.com/HDJgn2P.png)

And in this point we have a property
![](https://i.imgur.com/5OyLYRP.png)

That means we have a new visit created, but is not finished yet
![](https://i.imgur.com/zxugWRL.png)


To close the current visit we have to go out of the radio of the current property

Let's out of the radius of the current property

[POST]

http://localhost:4500/auth/users/location/

    {"latitude": 4.769902, "longitude": -74.032566}

![](https://i.imgur.com/TaZ5upj.png)

And now we have finished our visit
![](https://i.imgur.com/hi9GeXQ.png)


And now we have a new speed report
![](https://i.imgur.com/y5G7KvZ.png)

Let's see the detail of the last speed report
![](https://i.imgur.com/Mtyvw6m.png)
![](https://i.imgur.com/sxgxiOq.png)
![](https://i.imgur.com/QEfoZap.png)
![](https://i.imgur.com/C0qAvY9.png)

Now, we can know the routes of our user, the speeding, and more 

### Routes Description
In this endpoint we will get the routes for a day for a user
with these params with speed and speed

 - user_uuid (we have to go to the admin and copy the uuid)
 - date in this format (YYYY-MM-DD) example (2022-02-21)

Let's copy uuid in company users

![](https://i.imgur.com/fAbdZhu.png)

If you want, you can go to this endpoint and add the params

[POST]

http://localhost:4500/auth/users/{uuid}/routes/

[BODY]

    {"date": "2022-02-20"}

Let's back to the Browseable Api, and add the current date and user_uuid

![](https://i.imgur.com/kjL9HP4.png)


this will be the result

    {
    "current_page": 1,
    "pages": 1,
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "uuid": "adf2b241-5c48-4490-b8d7-056ae490e256",
            "location_start": {
                "latitude": 4.769813,
                "longitude": -74.027205
            },
            "location_end": {
                "latitude": 4.768804,
                "longitude": -74.032576
            },
            "speed_avg": 137,
            "max_speed": 375,
            "route": {
                "type": "LineString",
                "coordinates": [
                    [
                        -74.027205,
                        4.769813
                    ],
                    [
                        -74.030969,
                        4.769909
                    ],
                    [
                        -74.031006,
                        4.769433
                    ],
                    [
                        -74.032555,
                        4.769902
                    ],
                    [
                        -74.032576,
                        4.768804
                    ]
                ]
            },
            "speeding": [
                {
                    "speed": 375.93,
                    "current_limit": 50,
                    "difference": 325.93
                },
                {
                    "speed": 63.36,
                    "current_limit": 50,
                    "difference": 13.36
                },
                {
                    "speed": 161.55,
                    "current_limit": 50,
                    "difference": 111.55
                },
                {
                    "speed": 87.44,
                    "current_limit": 50,
                    "difference": 37.44
                }
            ]
        }
    ]

Now, we can see the route and the points with speed 

This endpoint already includes pagination

### Visits Description
In this endpoint we will get the routes for a day for a user
with these params with speed and speed

 - user_uuid (we have to go to the admin and copy the uuid)
 - date in this format (YYYY-MM-DD) example (2022-02-21)

Let's copy uuid in company users

![](https://i.imgur.com/fAbdZhu.png)

If you want, you can go to this endpoint and add the params

[POST]

http://localhost:4500/auth/users/{uuid}/visits/

[BODY]

    {"date": "2022-02-20"}

Let's back to the Browseable Api, and add the current date and user_uuid

![](https://i.imgur.com/H2K6MCW.png)


This will be the result

    {
      "current_page": 1,
      "pages": 1,
      "count": 1,
      "next": null,
      "previous": null,
      "results": [
          {
              "uuid": "3b179ebe-c97e-44cd-a773-030e007a7c63",
              "property": {
                  "uuid": "3f2385df-8a06-4ba0-9203-f645715e5390",
                  "address": "Cra 11A # 191A - 52",
                  "location": {
                      "latitude": 4.768804,
                      "longitude": -74.032578
                  }
              },
              "user": {
                  "uuid": "bda8d006-a050-4fc3-bf8f-bd1ee8bbfff8",
                  "username": "test",
                  "full_name": "oswaldo rodriguez"
              },
              "end_at": "20/02/2022 19:20:50",
              "created_at": "20/02/2022 19:07:23",
              "duration": "13 Minutes approx"
          }
      ] }


### Speed Limit Setup

Go back to setup in the admin page
![](https://i.imgur.com/BrdBNcr.png)

Here we can setup the speed limit and de displacement

Displacement it is to know which points to save depending on the 
difference in space, if I want to register the location every 50 meters, 
this is important because when there is heavy traffic and we have 
the location every 2 meters we will obtain many points and fill the 
database with information that we are not going to use then it is 
important to know the routes and travel times more than having all the 
points of a route without any meaning.


