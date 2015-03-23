#!/bin/sh
#

_script="$(readlink $0)"
BASEDIR="$(dirname $_script)"/..

MALLET_HOME=$BASEDIR/../mallet
MALLET_LIB=$MALLET_HOME/lib

export CLASSPATH=$BASEDIR/classifier/classes:$MALLET_HOME/class:$MALLET_LIB/mallet-deps.jar

if [ "$1" = make ] 
then
    shift
    $JAVAC -d $BASEDIR/classifier/classes "$@"
else 
    $JAVA -mx3000m MaxentClassifier "$@"
    # for cygwin
    # $JAVA -mx3000m -cp "$BASEDIR/classifier/classes;$MALLET_HOME/class;$MALLET_LIB/mallet-deps.jar" MaxentClassifier "$@"
    
fi
