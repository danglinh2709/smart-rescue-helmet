using NUnit.Framework;
using SmartRescueHelmet.Unity.Contracts;
using SmartRescueHelmet.Unity.Networking;

namespace SmartRescueHelmet.Unity.Tests.EditMode
{
    public sealed class RealtimeEnvelopeTests
    {
        [Test]
        public void Realtime_envelope_parser_recognizes_a_backend_telemetry_message()
        {
            const string payload = "{\"type\":\"telemetry\",\"device_id\":\"FF03\",\"timestamp\":\"2026-09-25T07:30:00+00:00\",\"data\":{\"sensors\":{\"temperature\":31.5}}}";

            var parsed = RealtimeEnvelopeParser.TryParse(payload, out var envelope);

            Assert.That(parsed, Is.True);
            Assert.That(envelope.MessageType, Is.EqualTo("telemetry"));
            Assert.That(envelope.DeviceId, Is.EqualTo("FF03"));
            Assert.That(envelope.Timestamp, Is.EqualTo("2026-09-25T07:30:00+00:00"));
        }

        [Test]
        public void Realtime_envelope_parser_rejects_an_unknown_message_type()
        {
            const string payload = "{\"type\":\"internal_debug\",\"data\":{}}";

            Assert.That(RealtimeEnvelopeParser.TryParse(payload, out _), Is.False);
        }
    }
}
