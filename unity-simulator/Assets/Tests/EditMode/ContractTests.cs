using NUnit.Framework;
using SmartRescueHelmet.Unity.Contracts;
using SmartRescueHelmet.Unity.Devices;
using System.Text.Json;

namespace SmartRescueHelmet.Unity.Tests.EditMode
{
public sealed class ContractTests
{
    [Test]
    public void Telemetry_factory_creates_a_valid_contract_payload()
    {
        var payload = HelmetMessages.CreateNormalTelemetry("FF01");

        Assert.That(JsonContractValidator.IsValid("telemetry.schema.json", payload), Is.True);
    }

    [TestCase("FF01", "telemetry", "helmet/FF01/telemetry")]
    [TestCase("FF02", "health", "helmet/FF02/health")]
    public void Topic_builder_uses_the_shared_contract(
        string deviceId,
        string messageType,
        string expected)
    {
        Assert.That(HelmetTopicBuilder.Build(deviceId, messageType), Is.EqualTo(expected));
    }

    [Test]
    public void Topic_builder_rejects_an_invalid_device_id()
    {
        Assert.That(
            () => HelmetTopicBuilder.Build("bad id", "telemetry"),
            Throws.ArgumentException);
    }

    [Test]
    public void Telemetry_factory_serializes_the_current_critical_sensor_snapshot()
    {
        var snapshot = new DeviceSensorSnapshot
        {
            Temperature = 61f,
            Co = 12f,
            Ax = .02f,
            Ay = .01f,
            Az = 9.81f,
            Battery = 72f,
            Movement = "WALKING",
        };

        var payload = HelmetMessages.CreateTelemetry(
            "FF03", snapshot, new LocalSafetyResult { RiskLevel = "CRITICAL" });

        Assert.That(JsonContractValidator.IsValid("telemetry.schema.json", payload), Is.True);
        using var document = JsonDocument.Parse(payload);
        Assert.That(document.RootElement.GetProperty("risk_level").GetString(), Is.EqualTo("CRITICAL"));
        Assert.That(document.RootElement.GetProperty("sensors").GetProperty("temperature").GetSingle(), Is.EqualTo(61f));
        Assert.That(document.RootElement.GetProperty("device").GetProperty("battery").GetSingle(), Is.EqualTo(72f));
    }

    [Test]
    public void Status_factory_serializes_current_fall_and_sos_state()
    {
        var snapshot = new DeviceSensorSnapshot { Fall = true, Sos = true, Movement = "UNUSUAL_MOVEMENT" };

        var payload = HelmetMessages.CreateStatus(
            "FF03", snapshot, new LocalSafetyResult { RiskLevel = "CRITICAL" });

        Assert.That(JsonContractValidator.IsValid("status.schema.json", payload), Is.True);
        using var document = JsonDocument.Parse(payload);
        Assert.That(document.RootElement.GetProperty("risk_level").GetString(), Is.EqualTo("CRITICAL"));
        Assert.That(document.RootElement.GetProperty("movement").GetString(), Is.EqualTo("UNUSUAL_MOVEMENT"));
        Assert.That(document.RootElement.GetProperty("fall").GetBoolean(), Is.True);
        Assert.That(document.RootElement.GetProperty("sos").GetBoolean(), Is.True);
    }
}
}
