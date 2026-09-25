using NUnit.Framework;
using SmartRescueHelmet.Unity.Networking;
using SmartRescueHelmet.Unity.Presentation;

namespace SmartRescueHelmet.Unity.Tests.EditMode
{
    public sealed class CommandCenterStateTests
    {
        [Test]
        public void Telemetry_envelope_updates_backend_device_state()
        {
            const string data = "{\"risk_level\":\"CRITICAL\",\"sensors\":{\"temperature\":61.5,\"co\":12.0},\"state\":{\"movement\":\"WALKING\"},\"device\":{\"battery\":72.0,\"wifi\":\"CONNECTED\",\"mqtt\":\"CONNECTED\"}}";
            var envelope = new RealtimeEnvelope("telemetry", "FF03", "2026-09-25T10:00:00+00:00", data);
            var state = new CommandCenterState();

            state.Apply(envelope);

            Assert.That(state.DeviceId, Is.EqualTo("FF03"));
            Assert.That(state.LastMessageType, Is.EqualTo("telemetry"));
            Assert.That(state.RiskLevel, Is.EqualTo("CRITICAL"));
            Assert.That(state.Temperature, Is.EqualTo(61.5f));
            Assert.That(state.Battery, Is.EqualTo(72f));
        }
    }
}
