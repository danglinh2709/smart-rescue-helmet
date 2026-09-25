using NUnit.Framework;
using SmartRescueHelmet.Unity.Contracts;

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
}
}
