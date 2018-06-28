#! /bin/bash

# Get current sensors
sensors=`ls /sys/bus/w1/devices/`
data="`date +%Y/%m/%d/%H:%M:%S`"

for i in $sensors; do
  if [ "$i" != "w1_bus_master1" ]
  then
    # Read Temperature
    tempread=`cat "/sys/bus/w1/devices/$i/w1_slave"`
    # Format
    temp=`echo "scale=2; "\`echo ${tempread##*=}\`" / 1000" | bc`
    if [ "$#" -ge 1 ]
    then
      data="$data,$temp"
    else
      echo "The measured temperature for $i is  $temp °C"
    fi
  fi
done

if [ "$#" -ge 1 ]
then
  #data="$data\n"
  `echo $data >> $1`
fi
