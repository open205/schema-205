# Data Types
| Data Type |                                                     Description                                                      | JSON Schema Type |          Examples           |
|-----------|----------------------------------------------------------------------------------------------------------------------|------------------|-----------------------------|
| Integer   | A positive or negative whole number (i.e., a number that can be written without a fractional part).                  | integer          | 3, 19, -4                   |
| Numeric   | A number that may include a fractional part with optional leading sign and optional exponent (engineering notation). | number           | 3.43, 0, -4, 1.03e4         |
| Boolean   | True or false.                                                                                                       | boolean          | true, false                 |
| String    | A sequence of characters of any length using any (specified) character set.                                          | string           | Indirect evaporative cooler |
| Null      | Indicator that no value is provided. Only used in combination with other data types, e.g., 'Number/Null'.            | null             | null                        |

# ConditioningType
|    Enumerator     |    Description    | Notes |
|-------------------|-------------------|-------|
| HEATED_AND_COOLED | Heated and cooled |       |
| HEATED_ONLY       | Heated only       |       |
| SEMIHEATED        | Semiheated        |       |
| UNCONDITIONED     | Unconditioned     |       |
| PLENUM            | Plenum            |       |

# UseClassType
|                              Enumerator                               |                                                Description                                                | Notes |
|-----------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|-------|
| AUTOMOTIVE_FACILITY                                                   | Automotive facility                                                                                       |       |
| CONVENTION_CENTER                                                     | Convention center                                                                                         |       |
| COURTHOUSE                                                            | Courthouse                                                                                                |       |
| DINING_BAR_LOUNGE_LEISURE                                             | Dining: Bar lounge/leisure                                                                                |       |
| DINING_CAFETERIA_FAST_FOOD                                            | Dining: Cafeteria/fast food                                                                               |       |
| DINING_FAMILY                                                         | Dining: Family                                                                                            |       |
| DORMITORY                                                             | Dormitory                                                                                                 |       |
| EXERCISE_CENTER                                                       | Exercise center                                                                                           |       |
| FIRE_STATION                                                          | Fire station                                                                                              |       |
| GYMNASIUM                                                             | Gymnasium                                                                                                 |       |
| HEALTH_CARE_CLINIC                                                    | Health-care clinic                                                                                        |       |
| HOSPITAL                                                              | Hospital                                                                                                  |       |
| HOTEL_MOTEL                                                           | Hotel/motel                                                                                               |       |
| LIBRARY                                                               | Library                                                                                                   |       |
| MANUFACTURING_FACILITY                                                | Manufacturing facility                                                                                    |       |
| MOTION_PICTURE_THEATER                                                | Motion picture theater                                                                                    |       |
| MULTIFAMILY                                                           | Multifamily                                                                                               |       |
| MUSEUM                                                                | Museum                                                                                                    |       |
| OFFICE                                                                | Office                                                                                                    |       |
| PARKING_GARAGE                                                        | Parking garage                                                                                            |       |
| PENITENTIARY                                                          | Penitentiary                                                                                              |       |
| PERFORMING_ARTS_THEATER                                               | Performing arts theater                                                                                   |       |
| POLICE_STATION                                                        | Police station                                                                                            |       |
| POST_OFFICE                                                           | Post office                                                                                               |       |
| RELIGIOUS_FACILITY                                                    | Religious facility                                                                                        |       |
| RETAIL                                                                | Retail                                                                                                    |       |
| SCHOOL_UNIVERSITY                                                     | School/university                                                                                         |       |
| SPORTS_ARENA                                                          | Sports arena                                                                                              |       |
| TOWN_HALL                                                             | Town hall                                                                                                 |       |
| TRANSPORTATION                                                        | Transportation                                                                                            |       |
| WAREHOUSE                                                             | Warehouse                                                                                                 |       |
| WORKSHOP                                                              | Workshop                                                                                                  |       |
| ATRIUM_LOW                                                            | Atrium - Low                                                                                              |       |
| ATRIUM_MEDIUM                                                         | Atrium - Medium                                                                                           |       |
| ATRIUM_HIGH                                                           | Atrium - High                                                                                             |       |
| AUDIENCE_SEATING_AREA_AUDITORIUM                                      | Audience Seating Area - Auditorium                                                                        |       |
| AUDIENCE_SEATING_AREA_GYMNASIUM                                       | Audience Seating Area - Gymnasium                                                                         |       |
| AUDIENCE_SEATING_AREA_MOTION_PICTURE_THEATER                          | Audience Seating Area - Motion picture theater                                                            |       |
| AUDIENCE_SEATING_AREA_PENITENTIARY                                    | Audience Seating Area - Penitentiary                                                                      |       |
| AUDIENCE_SEATING_AREA_PERFORMING_ARTS_THEATER                         | Audience Seating Area - Performing arts theater                                                           |       |
| AUDIENCE_SEATING_AREA_RELIGIOUS_FACILITY                              | Audience Seating Area - Religious facility                                                                |       |
| AUDIENCE_SEATING_AREA_SPORTS_ARENA                                    | Audience Seating Area - Sports arena                                                                      |       |
| AUDIENCE_SEATING_AREA_ALL_OTHER                                       | Audience Seating Area - All other                                                                         |       |
| BANKING_ACTIVITY_AREA                                                 | Banking Activity Area                                                                                     |       |
| CLASSROOM_LECTURE_HALL_TRAINING_ROOM_PENITENTIARY                     | Classroom/Lecture Hall/Training Room - Penitentiary                                                       |       |
| CLASSROOM_LECTURE_HALL_TRAINING_ROOM_ALL_OTHER                        | Classroom/Lecture Hall/Training Room - All other                                                          |       |
| CONFERENCE_MEETING_MULTIPURPOSE_ROOM                                  | Conference/Meeting/Multipurpose Room                                                                      |       |
| CONFINEMENT_CELLS                                                     | Confinement Cells                                                                                         |       |
| COPY_PRINT_ROOM                                                       | Copy/Print Room                                                                                           |       |
| CORRIDOR_FACILITY_FOR_THE_VISUALLY_IMPAIRED                           | Corridor - Facility for the visually impaired (and not used primarily by the staff)                       |       |
| CORRIDOR_HOSPITAL                                                     | Corridor - Hospital                                                                                       |       |
| CORRIDOR_ALL_OTHERS                                                   | Corridor - All others                                                                                     |       |
| COURT_ROOM                                                            | Court room                                                                                                |       |
| COMPUTER_ROOM                                                         | Computer Room                                                                                             |       |
| DINING_AREA_PENITENTIARY                                              | Dining Area - Penitentiary                                                                                |       |
| DINING_AREA_FACILITY_FOR_THE_VISUALLY_IMPAIRED                        | Dining Area - Facility for the visually impaired (and not used primarily by the staff)                    |       |
| DINING_AREA_BAR_LOUNGE_OR_LEISURE_DINING                              | Dining Area - Bar/lounge or leisure dining                                                                |       |
| DINING_AREA_CAFETERIA_OR_FAST_FOOD_DINING                             | Dining Area - Cafeteria or fast food dining                                                               |       |
| DINING_AREA_FAMILY_DINING                                             | Dining Area - Family dining                                                                               |       |
| DINING_AREA_ALL_OTHERS                                                | Dining Area - All others                                                                                  |       |
| ELECTRICAL_MECHANICAL_ROOM                                            | Electrical/Mechanical Room                                                                                |       |
| EMERGENCY_VEHICLE_GARAGE                                              | Emergency Vehicle Garage                                                                                  |       |
| FOOD_PREPARATION_AREA                                                 | Food Preparation Area                                                                                     |       |
| GUEST_ROOM                                                            | Guest Room                                                                                                |       |
| LABORATORY_IN_OR_AS_A_CLASSROOM                                       | Laboratory - In or as a classroom                                                                         |       |
| LABORATORY_ALL_OTHERS                                                 | Laboratory - All others                                                                                   |       |
| LAUNDRY_WASHING_AREA                                                  | Laundry/Washing Area                                                                                      |       |
| LOADING_DOCK_INTERIOR                                                 | Loading Dock, Interior                                                                                    |       |
| LOBBY_FACILITY_FOR_THE_VISUALLY_IMPAIRED                              | Lobby - Facility for the visually impaired (and not used primarily by the staff)                          |       |
| LOBBY_ELEVATOR                                                        | Lobby - Elevator                                                                                          |       |
| LOBBY_HOTEL                                                           | Lobby - Hotel                                                                                             |       |
| LOBBY_MOTION_PICTURE_THEATER                                          | Lobby - Motion picture theater                                                                            |       |
| LOBBY_PERFORMING_ARTS_THEATER                                         | Lobby - Performing arts theater                                                                           |       |
| LOBBY_ALL_OTHERS                                                      | Lobby - All others                                                                                        |       |
| LOCKER_ROOM                                                           | Locker Room                                                                                               |       |
| LOUNGE_BREAKROOM_HEALTH_CARE_FACILITY                                 | Lounge/Breakroom - Health care facility                                                                   |       |
| LOUNGE_BREAKROOM_ALL_OTHERS                                           | Lounge/Breakroom - All others                                                                             |       |
| OFFICE_ENCLOSED_AND_SMALL                                             | Office - Enclosed and small                                                                               |       |
| OFFICE_ENCLOSED_AND_LARGE                                             | Office - Enclosed and large                                                                               |       |
| OFFICE_OPEN_PLAN                                                      | Office - Open plan                                                                                        |       |
| PARKING_AREA_INTERIOR                                                 | Parking Area, Interior                                                                                    |       |
| PHARMACY_AREA                                                         | Pharmacy Area                                                                                             |       |
| RESTROOM_FACILITY_FOR_THE_VISUALLY_IMPAIRED                           | Restroom - Facility for the visually impaired (and not used primarily by the staff)                       |       |
| RESTROOM_ALL_OTHERS                                                   | Restroom - All others                                                                                     |       |
| SALES_AREA                                                            | Sales Area                                                                                                |       |
| SEATING_AREA_GENERAL                                                  | Seating Area, General                                                                                     |       |
| STAIRWAY                                                              | Stairway                                                                                                  |       |
| STAIRWELL                                                             | Stairwell                                                                                                 |       |
| STORAGE_ROOM_SMALL                                                    | Storage Room - Small                                                                                      |       |
| STORAGE_ROOM_LARGE                                                    | Storage Room - Large                                                                                      |       |
| VEHICULAR_MAINTENANCE_AREA                                            | Vehicular Maintenance Area                                                                                |       |
| FACILITY_FOR_THE_VISUALLY_IMPAIRED_CHAPEL                             | Facility for the Visually Impaired - Chapel (used primarily by residents)                                 |       |
| FACILITY_FOR_THE_VISUALLY_IMPAIRED_RECREATION_ROOM_COMMON_LIVING_ROOM | Facility for the Visually Impaired - Recreatio nroom/common living room (and not used primarily by staff) |       |
| CONVENTION_CENTER_EXHIBIT_SPACE                                       | Convention Center — Exhibit Space                                                                         |       |
| DORMITORY_LIVING_QUARTERS                                             | Dormitory — Living Quarters                                                                               |       |
| FIRE_STATION_SLEEPING_QUARTERS                                        | Fire Station — Sleeping Quarters                                                                          |       |
| GYMNASIUM_FITNESS_CENTER_EXERCISE_AREA                                | Gymnasium/Fitness Center - Exercise area                                                                  |       |
| GYMNASIUM_FITNESS_CENTER_PLAYING_AREA                                 | Gymnasium/Fitness Center - Playing area                                                                   |       |
| HEALTHCARE_FACILITY_EXAM_TREATMENT_ROOM                               | Healthcare Facility - Exam/treatment room                                                                 |       |
| HEALTHCARE_FACILITY_IMAGING_ROOM                                      | Healthcare Facility - Imaging room                                                                        |       |
| HEALTHCARE_FACILITY_MEDICAL_SUPPLY_ROOM                               | Healthcare Facility - Medical supply room                                                                 |       |
| HEALTHCARE_FACILITY_NURSERY                                           | Healthcare Facility - Nursery                                                                             |       |
| HEALTHCARE_FACILITY_NURSES_STATION                                    | Healthcare Facility - Nurse’s station                                                                     |       |
| HEALTHCARE_FACILITY_OPERATING_ROOM                                    | Healthcare Facility - Operating room                                                                      |       |
| HEALTHCARE_FACILITY_PATIENT_ROOM                                      | Healthcare Facility - Patient room                                                                        |       |
| HEALTHCARE_FACILITY_PHYSICAL_THERAPY_ROOM                             | Healthcare Facility - Physical therapy room                                                               |       |
| HEALTHCARE_FACILITY_RECOVERY_ROOM                                     | Healthcare Facility - Recovery room                                                                       |       |
| LIBRARY_READING_AREA                                                  | Library - Reading area                                                                                    |       |
| LIBRARY_STACKS                                                        | Library - Stacks                                                                                          |       |
| MANUFACTURING_FACILITY_DETAILED_MANUFACTURING_AREA                    | Manufacturing Facility - Detailed manufacturing area                                                      |       |
| MANUFACTURING_FACILITY_EQUIPMENTROOM                                  | Manufacturing Facility - Equipment room                                                                   |       |
| MANUFACTURING_FACILITY_EXTRA_HIGH_BAY_AREA                            | Manufacturing Facility - Extra high bay area                                                              |       |
| MANUFACTURING_FACILITY_HIGH_BAY_AREA                                  | Manufacturing Facility - High bay area                                                                    |       |
| MANUFACTURING_FACILITY_LOW_BAY_AREA                                   | Manufacturing Facility - Low bay area                                                                     |       |
| MUSEUM_GENERAL_EXHIBITION_AREA                                        | Museum - General exhibition area                                                                          |       |
| MUSEUM_RESTORATION_ROOM                                               | Museum - Restoration room                                                                                 |       |
| PERFORMING_ARTS_THEATER_DRESSING_ROOM                                 | Performing Arts Theater — Dressing Room                                                                   |       |
| POST_OFFICE_SORTING_AREA                                              | Post Office — Sorting Area                                                                                |       |
| RELIGIOUS_FACILITY_FELLOWSHIP_HALL                                    | Religious Facility - Fellowship hall                                                                      |       |
| RELIGIOUS_FACILITY_WORSHIP_PULPIT_CHOIR_AREA                          | Religious Facility - Worship/pulpit/choir area                                                            |       |
| RETAIL_FACILITIES_DRESSING_FITTING_ROOM                               | Retail Facilities - Dressing/fitting room                                                                 |       |
| RETAIL_FACILITIES_MALL_CONCOURSE                                      | Retail Facilities - Mall concourse                                                                        |       |
| SPORTS_ARENA_PLAYING_AREA_CLASS_I_FACILITY                            | Sports Arena — Playing Area - Class I facility                                                            |       |
| SPORTS_ARENA_PLAYING_AREA_CLASS_II_FACILITY                           | Sports Arena — Playing Area - Class II facility                                                           |       |
| SPORTS_ARENA_PLAYING_AREA_CLASS_III_FACILITY                          | Sports Arena — Playing Area - Class III facility                                                          |       |
| SPORTS_ARENA_PLAYING_AREA_CLASS_IV_FACILITY                           | Sports Arena — Playing Area - Class IV facility                                                           |       |
| TRANSPORTATION_FACILITY_BAGGAGE_CAROUSEL_AREA                         | Transportation Facility - Baggage/carousel area                                                           |       |
| TRANSPORTATION_FACILITY_AIRPORT_CONCOURSE                             | Transportation Facility - Airport concourse                                                               |       |
| TRANSPORTATION_FACILITY_TICKET_COUNTER                                | Transportation Facility - Ticket counter                                                                  |       |
| WAREHOUSE_STORAGE_AREA_MEDIUM_TO_BULKY_PALLETIZED_ITEMS               | Warehouse — Storage Area - Medium to bulky, palletized items                                              |       |
| WAREHOUSE_STORAGE_AREA_SMALLER_HAND_CARRIED_ITEMS                     | Warehouse — Storage Area - Smaller, hand-carried items                                                    |       |

# TransformerType
|  Enumerator  | Description  | Notes |
|--------------|--------------|-------|
| DRY_TYPE     | Dry Type     |       |
| FLUID_FILLED | Fluid Filled |       |
| OTHER        | Other        |       |

# TransformerPhase
|  Enumerator  | Description  | Notes |
|--------------|--------------|-------|
| SINGLE_PHASE | Single Phase |       |
| THREE_PHASE  | Three Phase  |       |

# ASHRAE229
|    Data Element Name     |                                              Description                                              |         Data Type         | Units | Range | Req |                                                                             Notes                                                                              |
|--------------------------|-------------------------------------------------------------------------------------------------------|---------------------------|-------|-------|-----|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| transformers             | Electrical transformers at the building site                                                          | [{Transformer}]           |       |       |     | Contains a list of transformers that convert electricity from a higher voltage to one used by the building, exterior lighting, and other services at the site. |
| buildings                | Buildings on the site                                                                                 | [{Building}]              |       |       |     | Contains a list of buildings on the site (often just one).                                                                                                     |
| spaces                   | Spaces in the building                                                                                | [{Space}]                 |       |       |     | Contains a list of spaces in the building.                                                                                                                     |
| schedules                | Schedules for internal loads, thermostats, equipment operation and control, and any other need.       | [{Schedule}]              |       |       |     | Contains a list of schedules used in model.                                                                                                                    |
| schedules_alternative_01 | Alternative way of expressing schedules with only a few key values including a fingerprint-hash value | [{ScheduleAlternative01}] |       |       |     | Contains a list of schedules used in model.                                                                                                                    |

# Building
| Data Element Name |         Description          | Data Type | Units | Range | Req | Notes |
|-------------------|------------------------------|-----------|-------|-------|-----|-------|
| id                | Unique Identification Number | Numeric   |       |       | ✓   |       |
| name              | Name of the Building         | String    |       |       | ✓   |       |
| number_of_floors  | Number of floors             | Numeric   |       | >=0   | ✓   |       |

# Space
| Data Element Name |                                                                                                                                                                                                                           Description                                                                                                                                                                                                                           |     Data Type      | Units | Range | Req | Notes |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|-------|-------|-----|-------|
| id                | Unique Identification Number                                                                                                                                                                                                                                                                                                                                                                                                                                    | Numeric            |       |       | ✓   |       |
| name              | Name fo the Space                                                                                                                                                                                                                                                                                                                                                                                                                                               | String             |       |       | ✓   |       |
| floor_area        | The floor area of a space within the building, including basements, mezzanine and intermediate-floored tiers, and penthouses with a headroom height of 7.5 ft or greater. It is measured from the exterior faces of walls or from the center-line of walls separating buildings, but excluding covered walkways, open roofed-over areas, porches and similar spaces, pipe trenches, exterior terraces or steps, chimneys, roof overhangs, and similar features. | Numeric            |       | >=0   | ✓   |       |
| conditioning_type | Space conditioning category                                                                                                                                                                                                                                                                                                                                                                                                                                     | <ConditioningType> |       |       | ✓   |       |
| use_class         | Whether space use types are building area types from Table 9.5.1 or space use types from Table 9.6.1                                                                                                                                                                                                                                                                                                                                                            | <UseClassType>     |       |       | ✓   |       |

# Transformer
| Data Element Name |                             Description                              |     Data Type      | Units | Range | Req | Notes |
|-------------------|----------------------------------------------------------------------|--------------------|-------|-------|-----|-------|
| name              | Transformer Name                                                     | String             |       |       | ✓   |       |
| type              | The type of transformer                                              | <TransformerType>  |       |       | ✓   |       |
| phase             | The number of electrical phases                                      | <TransformerPhase> |       |       | ✓   |       |
| efficiency        | Transformer efficiency                                               | Numeric            |       | >=0   | ✓   |       |
| capacity          | Rated Capacity of the Transformer                                    | Numeric            | Va    | >=0   | ✓   |       |
| peak_load         | Annual Peak electric load on the transformer                         | Numeric            | W     | >=0   | ✓   |       |
| capacity_ratio    | Annual Peak electric load of the transformer divided by the capacity | Numeric            |       | >=0   | ✓   |       |

# Schedule
| Data Element Name |                Description                |    Data Type     | Units | Range | Req |                                             Notes                                              |
|-------------------|-------------------------------------------|------------------|-------|-------|-----|------------------------------------------------------------------------------------------------|
| id                | Unique Identification Number              | Numeric          |       |       | ✓   |                                                                                                |
| name              | Name of the Schedule                      | String           |       |       | ✓   |                                                                                                |
| type              | The type of schedule                      | String           |       |       | ✓   | Not an enumerations because we only care that the type assigned by BEM tool matches across RMR |
| week_schedules    | List of week schedules in annual schedule | [{WeekSchedule}] |       |       |     | Contains a list of week specficiations                                                         |

# WeekSchedule
|        Data Element Name        |             Description              |   Data Type   | Units |   Range   | Req | Notes |
|---------------------------------|--------------------------------------|---------------|-------|-----------|-----|-------|
| id                              | Unique Identification Number         | Numeric       |       |           | ✓   |       |
| name                            | Week Schedule Name                   | String        |       |           | ✓   |       |
| start_month                     | start month of assigned weeks        | Integer       |       | >=1, <=12 | ✓   |       |
| start_day                       | start day of month of assigned weeks | Integer       |       | >=1, <=31 | ✓   |       |
| end_month                       | end month of assigned weeks          | Integer       |       | >=1, <=12 | ✓   |       |
| end_day                         | end day of month of assigned weeks   | Integer       |       | >=1, <=31 | ✓   |       |
| monday_day_schedule             | Monday Schedule Name                 | {DaySchedule} |       |           | ✓   |       |
| tuesday_day_schedule            | Tuesday Schedule Name                | {DaySchedule} |       |           | ✓   |       |
| wednesday_day_schedule          | Wednesday Schedule Name              | {DaySchedule} |       |           | ✓   |       |
| thursday_day_schedule           | Thursday Schedule Name               | {DaySchedule} |       |           | ✓   |       |
| friday_day_schedule             | Friday Schedule Name                 | {DaySchedule} |       |           | ✓   |       |
| saturday_day_schedule           | Saturday Schedule Name               | {DaySchedule} |       |           | ✓   |       |
| sunday_day_schedule             | Sunday Schedule Name                 | {DaySchedule} |       |           | ✓   |       |
| holiday_day_schedule            | Holiday Schedule Name                | {DaySchedule} |       |           | ✓   |       |
| cooling_design_day_day_schedule | Cooling design day Schedule Name     | {DaySchedule} |       |           | ✓   |       |
| heating_design_day_day_schedule | Heating design day Schedule Name     | {DaySchedule} |       |           | ✓   |       |

# DaySchedule
| Data Element Name |         Description          |    Data Type     | Units | Range | Req | Notes |
|-------------------|------------------------------|------------------|-------|-------|-----|-------|
| id                | Unique Identification Number | Numeric          |       |       | ✓   |       |
| name              | Name of the Day Schedule     | String           |       |       | ✓   |       |
| values            | Hourly Values of Schedule    | [Numeric][1..24] |       |       | ✓   |       |

# ScheduleAlternative01
|                 Data Element Name                 |                                        Description                                         | Data Type | Units | Range | Req |                                                                                Notes                                                                                 |
|---------------------------------------------------|--------------------------------------------------------------------------------------------|-----------|-------|-------|-----|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| id                                                | Unique Identification Number                                                               | Numeric   |       |       | ✓   |                                                                                                                                                                      |
| name                                              | Name of the Schedule                                                                       | String    |       |       | ✓   |                                                                                                                                                                      |
| type                                              | The type of schedule                                                                       | String    |       |       | ✓   | Not an enumerations because we only care that the type assigned by BEM tool matches across RMR                                                                       |
| hash_fingerprint                                  | A digital fingerprint or hash of all schedule values                                       | Integer   |       |       | ✓   | The hash algorithm would need to result in significant different hash values when only minor changes are made to the schedule and is primarily to check for sameness |
| equivalent_full_load_hours                        | Equivalent full load hours                                                                 | Numeric   |       |       | ✓   | The sum of the schedule values for entire year                                                                                                                       |
| average_value                                     | The average value of the schedule                                                          | Numeric   |       |       | ✓   | the average value of schedule for all hours in the schedule                                                                                                          |
| average_occupied_value                            | The average value of the schedule during occupied hours                                    | Numeric   |       |       | ✓   | The occupied and unoccupied time periods are defined elsewhere.                                                                                                      |
| average_unoccupied_value                          | The average value of the schedule during unoccupied hours                                  | Numeric   |       |       | ✓   | The occupied and unoccupied time periods are defined elsewhere.                                                                                                      |
| fraction_of_occupied_hours_nonzero                | Fraction of the occupied hours that are nonzero or 'on'                                    | Numeric   |       |       | ✓   | The occupied and unoccupied time periods are defined elsewhere.                                                                                                      |
| fraction_of_unoccupied_hours_nonzero              | Fraction of the unoccupied hours that are nonzero or 'on'                                  | Numeric   |       |       | ✓   | The occupied and unoccupied time periods are defined elsewhere.                                                                                                      |
| most_common_occupied_hour_value                   | Most common value of schedule during occupied hours                                        | Numeric   |       |       | ✓   | The occupied and unoccupied time periods are defined elsewhere.                                                                                                      |
| most_common_unoccupied_hour_value                 | Most common value of schedule during unoccupied hours                                      | Numeric   |       |       | ✓   | The occupied and unoccupied time periods are defined elsewhere.                                                                                                      |
| fraction_of_occupied_hours_at_most_common_value   | Fraction of the occupied hours that are at the most common value during occupied hours     | Numeric   |       |       | ✓   | The occupied and unoccupied time periods are defined elsewhere.                                                                                                      |
| fraction_of_unoccupied_hours_at_most_common_value | Fraction of the unoccupied hours that are at the most common value during unoccupied hours | Numeric   |       |       | ✓   | The occupied and unoccupied time periods are defined elsewhere.                                                                                                      |

