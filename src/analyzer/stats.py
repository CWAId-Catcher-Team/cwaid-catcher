import os
import utils.statistics_pb2 as statistics_pb2


# Returns a dictionary containing the statistics of each day as a further dictionary
def stats_parser():
    # Store statistics for each day in here
    all_stats = dict()
    
    # Iterate over all stats files to parse
    for subdir, dirnames, filenames in os.walk("../puller/export_stats"):
        for f in os.listdir(subdir):
            if f == "export.bin":
                with open(os.path.join(subdir, f), "rb") as f_tmp:
                    content = f_tmp.read()

                # Convert bytes to statistics
                stat = statistics_pb2.Statistics()
                stat.ParseFromString(content)

                # Write all values into dictionary for easy access
                stats_dict = dict()

                for keyFigureCard in stat.keyFigureCards:
                    # Different values are stored here e.g. new infections and average over 7 days
                    keyFigures = keyFigureCard.keyFigures

                    # New infections 
                    if keyFigureCard.header.cardId == 1: 
                        for keyFigure in keyFigures:
                            # Primary = amount of new infections on that day
                            if keyFigure.rank == 1:
                                stats_dict["new_infections"] = keyFigure.value
                            # Secondary = 7 day average of new infections 
                            elif keyFigure.rank == 2:
                                stats_dict["new_infections_7_day_average"] = keyFigure.value
                            # Tertiary = Total infections 
                            elif keyFigure.rank == 3:
                                stats_dict["total_infections"] = keyFigure.value
                    # 7 day incidence value
                    elif keyFigureCard.header.cardId == 2: 
                        for keyFigure in keyFigures:
                            # Primary = 7 days incidence 
                            if keyFigure.rank == 1:
                                stats_dict["7_day_incidence"] = keyFigure.value
                    # Warnings by App users
                    elif keyFigureCard.header.cardId == 3: 
                        for keyFigure in keyFigures:
                            # Primary = Warnings by app users on that day 
                            if keyFigure.rank == 1:
                                stats_dict["new_cwa_warnings"] = keyFigure.value
                            # Secondary = 7 day average of new warnings
                            elif keyFigure.rank == 2:
                                stats_dict["new_cwa_warnings_7_day_average"] = keyFigure.value
                            # Tertiary = Total warnings 
                            elif keyFigure.rank == 3:
                                stats_dict["total_cwa_warnings"] = keyFigure.value
                    # 7 day R value
                    elif keyFigureCard.header.cardId == 4: 
                        for keyFigure in keyFigures:
                            # Primary = 7 day R value 
                            if keyFigure.rank == 1:
                                stats_dict["7_day_r_value"] = keyFigure.value

                # Check if all values were found
                if len(stats_dict) != 8:
                    print("Error parsing stats. Exiting.")
                    exit(1)

                date_name = os.path.basename(subdir)
                all_stats[date_name] = stats_dict

    return all_stats


def print_stats(all_stats):
    dates = []
    for date in all_stats.keys():
        dates.append(date)
    dates.sort()

    for date in dates:
        stat_dict = all_stats[date]
        print("[" + date + "] New CWA warnings: " + str(stat_dict["new_cwa_warnings"]))
        print("[" + date + "] New CWA warnings 7-day average: " + str(stat_dict["new_cwa_warnings_7_day_average"]))
        print("[" + date + "] Total CWA warnings: " + str(stat_dict["total_cwa_warnings"]))
        print("[" + date + "] New infections: " + str(stat_dict["new_infections"]))
        print("[" + date + "] New infections 7-day average: " + str(stat_dict["new_infections_7_day_average"]))
        print("[" + date + "] Total infections: " + str(stat_dict["total_infections"]))
        print("[" + date + "] 7-day incidence: " + str(stat_dict["7_day_incidence"]))
        print("[" + date + "] 7-day R value: " + str(stat_dict["7_day_r_value"]))
        print()


if __name__ == "__main__":    
    all_stats = stats_parser()
    print_stats(all_stats)
    print("Note: All values are exactly of the displayed day. E.g. for the day 2021-02-08 the new CWA warnings are the amount of warnings the CWA received on exactly that whole day.") 
