namespace SmartRescueHelmet.Unity.Devices
{
    public sealed class DeviceSensorSnapshot
    {
        public float Temperature;
        public float Co;
        public float Ax, Ay, Az, Gx, Gy, Gz;
        public float Battery;
        public bool Fall, Immobile, Sos;
        public string Movement = "WALKING";
        public string Wifi = "CONNECTED";
        public string Mqtt = "CONNECTED";
    }
}
