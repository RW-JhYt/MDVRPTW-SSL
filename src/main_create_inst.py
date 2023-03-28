"""
Create new type of instances
"""
import os
import random
import math
base_path = os.getcwd()

seed = 1200
write_path = base_path + r"\InstancesSchenker\Inst8"
depots = [2, 4]
n_same_inst = 3
cust_arr = range(5, 30, 5)  # 5 to 25

customers = [n_cust for n_cust in cust_arr for _ in range(n_same_inst)]

tight_tws_percentage = 0.10   # 10% of tight tw's
n_sls_between_depots = 6      # Number of SL to each depot from other depots
relax = 1.2                   # + 10% extra time
relax_vehs = 1.0              # 2 times as many vehs
big_order_percentage = 1/20
random.seed(seed)

if n_sls_between_depots % 2 != 0:
    print("Number of scheduled lines has be able to be divided by two")
    quit(0)

N_EXTRA_SL = 3  # Generate 3 more sls intervals but delete the middle 3
# this is how we get more feasible scheduled lines.
sls_to_keep = list(range(0, n_sls_between_depots + N_EXTRA_SL))
for _ in range(N_EXTRA_SL):
    del sls_to_keep[int(n_sls_between_depots/2)]


ctr = 0
n_customers_old = -1
for n_depots in depots:
    for n_customers in customers:
        if n_customers != n_customers_old:
            file_counter = 0
        vehicle_types = [
            ["0", "150", "1", "80", "3200", "2400", "2800", "54000", "22000"],
            ["1", "200", "1.25", "50", "13600", "11200", "12800", "54000", "32400"]
        ]
        ranges = [[51.975857, 4.809808],
                  [52.240695, 5.449762]]

        Sls = {
            "cost": "10",
            "capacity": "12000"
        }
        time_hor = [0, 24 * 3600]
        sl_speed = 40                # km/h on average
        SPACES = 12

        quantities = [random.randint(50, 1500) for _ in range(n_depots + n_customers)]
        total_quantities = sum(quantities)

        # Determine number of vehicles based on capacities
        n_busses = math.ceil(relax_vehs * 0.5 * (total_quantities / int(vehicle_types[0][4])))
        n_trucks = math.ceil(relax_vehs * 0.5 * (total_quantities / int(vehicle_types[1][4])))
        depots = {depot_idx: [n_busses, n_trucks] for depot_idx in range(n_depots)}

        def haversine_distance(lat1, lon1, lat2, lon2):
            """ Source: https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
            Calculate the great circle distance in kilometers between two points
            on the earth (specified in decimal degrees)
            """
            # convert decimal degrees to radians
            lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

            # haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            r = 6371  # Radius of earth in kilometers.
            return c * r

        n_vehicle_types = len(vehicle_types)
        n_number_of_vehs = n_depots * n_vehicle_types
        n_sls = n_sls_between_depots * n_depots * (n_depots - 1)
        n_nodes = n_depots + n_customers

        # Generate vehicle types
        vehicle_types_str = "[Vehicle Types] - ID_veh_type, fixed_cost, variable_cost, Speed, Capacity, alpha, beta, max_time, max_drive_time\n"
        for veh_type in vehicle_types:
            for elem in veh_type:
                vehicle_types_str += f"{elem:>{SPACES}}"
            vehicle_types_str += "\n"

        # Generate vehicle availability
        veh_type_av_str = "[Number of Vehicle Types] - ID_veh_type, ID_depot, number_of_vehicles\n"
        for depot_id, vehicle_types_availabilities in depots.items():
            for veh_type_id, veh_type_av in enumerate(vehicle_types_availabilities):
                veh_type_av_str += f"{veh_type_id:>{SPACES}}{depot_id:>{SPACES}}{veh_type_av:>{SPACES}}"
                veh_type_av_str += "\n"

        # Generate depot locations and customers
        nodes_write_str = "[Nodes/requests]: ID_node, ID_depot, lat, long, type, service_time, q_del, q_col, tw_depot_start,"
        nodes_write_str += " tw_depot_end, tw_cust_start, tw_cust_end\n"
        depot_coords = []
        for node_id in range(0, n_depots + n_customers):
            # General data
            latitude = round(random.uniform(ranges[0][0], ranges[1][0]), 3)
            longitude = round(random.uniform(ranges[0][1], ranges[1][1]), 3)

            # Type specific data
            if node_id < n_depots:
                node_type = "depot"
                service_time = 0
                q_del = 0
                q_col = 0
                depot_id = node_id
                depot_tw_start = time_hor[0]
                depot_tw_end = time_hor[1]
                cust_tw_start = time_hor[0]
                cust_tw_end = time_hor[1]
                depot_coords.append((latitude, longitude))
            else:
                is_big_order = random.random()
                if is_big_order:
                    service_time = 600 + 120 * random.randint(5, 15)  # Random 1 to 5 pieces
                    quantity = quantities[node_id] * random.randint(1, 4)
                else:
                    service_time = 600 + 120 * random.randint(0, 5)  # Random 1 to 5 pieces
                    quantity = quantities[node_id]

                depot_id = random.randint(0, n_depots - 1)
                is_collect = random.randint(0, 1)
                has_tight_tw = random.random()
                assigned_depot_coordinates = depot_coords[depot_id]
                direct_drive_dist = int(math.ceil(haversine_distance(assigned_depot_coordinates[0],
                                                     assigned_depot_coordinates[1],
                                                     latitude,
                                                     longitude)))
                direct_drive_time = round((direct_drive_dist/int(vehicle_types[0][3])) * 3600) # Bus speed

                if has_tight_tw < tight_tws_percentage:                     # has tight tw
                    cust_tw_start = random.randint(7 * 3600, 16 * 3600)     # UPDATE: random open small tw
                    cust_tw_length = random.randint(2400, 4 * 3600)
                    cust_tw_end = cust_tw_start + cust_tw_length
                else:  # Open all day
                    cust_tw_start = random.randint(7 * 3600, 12 * 3600)     # opens in the morning
                    cust_tw_end = 18 * 3600                                 # closes at 17.00

                if is_collect:
                    node_type = "collect"
                    q_del = 0
                    q_col = quantity
                    depot_tw_start = time_hor[0]                           # dummy
                    max_release_time = cust_tw_end + direct_drive_time              # Minimal time needed for feasibility
                    depot_tw_end = random.randint(min(round(max_release_time * relax),time_hor[1]),
                                                  time_hor[1])
                else:
                    node_type = "distribute"
                    q_col = 0
                    q_del = quantity
                    min_deadline_time = cust_tw_start - direct_drive_time
                    depot_tw_start = random.randint(0,
                                                    max(round(min_deadline_time/relax),0))           # Order arrives between 0 and 12 hour
                    depot_tw_end = time_hor[1]

            # Save the nodes
            nodes_write_str += f"{node_id:>{SPACES}}{depot_id:>{SPACES}}{latitude:>{SPACES}.3f}{longitude:>{SPACES}.3f}"
            nodes_write_str += f"{node_type:>{SPACES}}{service_time:>{SPACES}}{q_del:>{SPACES}}{q_col:>{SPACES}}"
            nodes_write_str += f"{depot_tw_start:>{SPACES}}{depot_tw_end:>{SPACES}}{cust_tw_start:>{SPACES}}"
            nodes_write_str += f"{cust_tw_end:>{SPACES}}\n"

        # Generate Scheduled
        sl_str = "[Scheduled Lines] - ID_from, ID_to, cost_per_req, capacity, dep_time, arr_time\n"
        for depot_idx1 in depots.keys():
            for depot_idx2 in depots.keys():
                if depot_idx1 == depot_idx2:
                    continue  # No SLs from and to same depot
                distance_km = haversine_distance(depot_coords[0][0],  # lat 1
                                                 depot_coords[0][1],  # lon 1
                                                 depot_coords[1][0],  # lat 2
                                                 depot_coords[1][1])  # lon 2
                travel_time = round((distance_km / sl_speed) * 3600)
                latest_dep_time = time_hor[1] - travel_time
                for sl_idx in sls_to_keep:
                    start_possible_dep_time = max(round(
                        (sl_idx / (n_sls_between_depots + N_EXTRA_SL + 1)) * time_hor[1]
                    ) - 1, 0)
                    end_possible_dep_time = round(
                        ((sl_idx + 1) / (n_sls_between_depots + N_EXTRA_SL + 1)) * time_hor[1]
                    ) - 1
                    rand_dep_time = random.randint(start_possible_dep_time,
                                                   end_possible_dep_time)
                    dep_time = min(rand_dep_time, latest_dep_time)
                    arr_time = dep_time + travel_time  # Always in time interval

                    sl_str += f"{depot_idx1:>{SPACES}}{depot_idx2:>{SPACES}}"
                    sl_str += f"{Sls['cost']:>{SPACES}}{Sls['capacity']:>{SPACES}}"
                    sl_str += f"{dep_time:>{SPACES}}{arr_time:>{SPACES}}\n"

        # Now write file by putting it all together
        inst_name = f"T_{n_depots}_{n_sls_between_depots}_{n_customers}_[{file_counter}]"

        write_str = f"{inst_name} {n_vehicle_types} {n_number_of_vehs} {n_sls} {n_nodes}\n"
        write_str += "\n"
        write_str += vehicle_types_str
        write_str += "\n"
        write_str += veh_type_av_str
        write_str += "\n"
        write_str += sl_str
        write_str += "\n"
        write_str += nodes_write_str
        write_str = write_str.rstrip()

        final_path = write_path + fr"\{inst_name}.txt"

        with open(final_path, 'w') as f:
            f.write(write_str)

        file_counter += 1
        n_customers_old = n_customers
