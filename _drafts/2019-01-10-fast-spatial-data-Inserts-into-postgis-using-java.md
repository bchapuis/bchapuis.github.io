---
layout: default
title: "Fast spatial data inserts into Postgis using Java and the COPY command (PgBulkInsert)"
date: 2019-01-10 09:49:00
---

## Fast spatial data inserts into Postgis using Java and the COPY command (PgBulkInsert)

Looking for a mean to efficiently import [OpenStreetMap](https://www.openstreetmap.org) data into [Postgis](https://postgis.net/) from Java, I recently came across [PgBulkInsert](https://github.com/bytefish/PgBulkInsert), a Java library that leverages the COPY command and comes with a single dependency to the official postgresql driver.
As the API is well thought and provides good extension points, this post will show how Postgis geometry data types can be supported with a few lines of cod.

PgBulkInsert use the COPY command with the [binary format](https://www.postgresql.org/docs/9.3/sql-copy.html) of Postgres to import data.
Implementing binary formats is often time consuming.
Luckily, Postgis extensively rely on the Well-Known Binary format ([WKB](https://en.wikipedia.org/wiki/Well-known_text#Well-known_binary)) implemented in many spatial libraries. 
Therefore, we can use an open source implementation of the format, such as the [Simple Features WKB](https://github.com/ngageoint/simple-features-wkb-java) maintained by the [National Geospatial-Intelligence Agency (NGA)](https://www.nga.mil/Pages/Default.aspx).

As a consequence, our project only needs the following two dependencies to import postgis geometry data types into Postgis.

```xml
<dependency>
    <groupId>de.bytefish</groupId>
    <artifactId>pgbulkinsert</artifactId>
    <version>3.3</version>
</dependency>
<dependency>
    <groupId>mil.nga.sf</groupId>
    <artifactId>sf-wkb</artifactId>
    <version>2.0.0</version>
</dependency>
```

To persist Java objects into Postgres, PgBulkInsert introduces an abstract utility class named `AbstractMapping` that can be used to map the properties of an objects, such as an `Integer`, a `Double` or a `String`, to the columns of a table.
As this class does not natively provide helpers to map the geometry data types of Postgis, we need to extend it.

```java
import de.bytefish.pgbulkinsert.mapping.AbstractMapping;
import de.bytefish.pgbulkinsert.pgsql.handlers.IValueHandlerProvider;
import mil.nga.sf.Geometry;

import java.util.function.Function;

public class GeometryMapping<T> extends AbstractMapping<T> {

    protected GeometryMapping(String schemaName, String tableName) {
        super(schemaName, tableName);
    }

    protected GeometryMapping(
            IValueHandlerProvider provider, 
            String schemaName, 
            String tableName) {
        super(provider, schemaName, tableName);
    }

    public void mapGeometry(
            String columnName, 
            Function<T, Geometry> propertyGetter) {
        map(columnName, new GeometryValueHandler(), propertyGetter);
    }
}
```

Here, the `Geometry` interface corresponds to any geometry described in the [Simple Feature Specification](https://www.opengeospatial.org/standards/sfa), such as a `Point`, a `LineString`, a `Polygon`, or any feature depicted in the Figure below.

![Geometry Class Hierarchy](/img/geometry-class-hierarchy.png)

The following `ValueHandler` generically serialize classes that implements the `Geometry` interface in a binary format that can be understood by Postgis.
Notice that, as mentionned in the Postgis [documentation](http://www.postgis.net/docs/ST_AsBinary.html), the protocol defaults to the endianness of the server.
As most microprocessors have a little-endian architecture, we hard code the endianness into the handler.

```java
import de.bytefish.pgbulkinsert.pgsql.handlers.BaseValueHandler;
import mil.nga.sf.Geometry;
import mil.nga.sf.util.ByteWriter;
import mil.nga.sf.wkb.GeometryWriter;

import java.io.DataOutputStream;
import java.nio.ByteOrder;

public class GeometryValueHandler extends BaseValueHandler<Geometry> {

    @Override
    protected void internalHandle(
            DataOutputStream buffer, 
            Geometry value) throws Exception {
        ByteWriter writer = new ByteWriter();
        writer.setByteOrder(ByteOrder.LITTLE_ENDIAN);
        GeometryWriter.writeGeometry(writer, value);
        byte[] wkb = writer.getBytes();
        buffer.writeInt(wkb.length);
        buffer.write(wkb);
    }
}
```

That's it, all necessary the plumbing to efficiently insert spatial data into Postgis is in place.
The following snippet demonstrates how to open the water to flood your database with geometries.

```java 
public class Main {
    
    public static class Place {
        public String getName();
        public Point getLocation();
    }

    public static class PlaceMapping extends GeometryMapping {
        public PlaceMapping() {
            super("public", "places");
            mapString("", Place::getName)
            mapGeometry("", Place::getLocation)
        }
    }

    public static void main(String[] args) {
        List<Place> places = new ArrayList<>();
        // ...
        PgBulkInsert insert = new PgBulkInsert(new PlaceMapping())
        insert.saveAll(places);
    }
}
```

In conclusion, this post showed how easilly PgBulkInsert can be leveraged to import spatial data into Postgis.
I have not precisely benchmarked PgBulkInsert yet, however preliminary results show a great performence gain when compared with the usual INSERT queries.
For instance, importing the OSM data for switzerland takes less than a minute on my desktop computer.

