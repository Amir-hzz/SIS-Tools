import arcpy
import os

def project_mosaic_footprint(root_path, output_shapefile):
    for root, _, files in os.walk(root_path):
        for file in files:
            if file.endswith(".ecw"):
                file_name = os.path.splitext(file)[0]
                output_file_path = os.path.join(root, file_name)
                file_does_not_exist = file_name not in [row[0] for row in arcpy.da.SearchCursor(output_shapefile, "WWW")]

                if file_does_not_exist:
                    input_raster = os.path.join(root, file)
                    print(f"Processing {input_raster}")

                    try:
                        arcpy.management.MakeRasterLayer(input_raster, file_name)
                        print(f"Added {file} to the map")
                    except arcpy.ExecuteError:
                        print(f"Failed to open {file}. Skipping...")
                        continue

                    # Other processing steps...
                    # Simplify the polygon to reduce the number of vertices
                    arcpy.cartography.SimplifyPolygon("Eliminated_polygon.shp", "simplified_polygon.shp", "POINT_REMOVE", "100 Meters")
                    
                    # Spatial reference
                    Template_sr = arcpy.SpatialReference(3308)
                    if arcpy.Describe("simplified_polygon.shp").spatialReference.name == "Unknown":
                        arcpy.management.DefineProjection("simplified_polygon.shp", Template_sr)

                    # Project the polygon to match the spatial reference of the layer
                    arcpy.management.Project("simplified_polygon.shp", "projected_polygon.shp", Template_sr)

                    # Append the polygon to the output shapefile
                    arcpy.Append_management("projected_polygon.shp", output_shapefile, "NO_TEST")

                    # Define the attribute values for the new polygon
                    field_name = "WWW"
                    field_value = file_name

                    # Update the last row of the attribute table
                    with arcpy.da.UpdateCursor(output_shapefile, field_name) as cursor:
                        for i, row in enumerate(cursor):
                            if i == len(list(cursor)) - 1:
                                row[0] = field_value
                                cursor.updateRow(row)

                    print(f"{file} footprint added")
                    
                    # Clean up temporary files
                    arcpy.Delete_management("out_polygon.shp")
                    arcpy.Delete_management("simplified_polygon.shp")
                    arcpy.Delete_management("Eliminated_polygon.shp")
                    arcpy.Delete_management("Dissolved_polygon.shp")
                    arcpy.Delete_management("projected_polygon.shp")

    print("Processing complete.")
