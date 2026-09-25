using System.Threading;
using System.Threading.Tasks;

namespace SmartRescueHelmet.Unity.Networking
{
    public interface IDeviceTransport
    {
        bool IsConnected { get; }
        Task<bool> PublishAsync(string topic, string payload, int qos, CancellationToken cancellationToken);
    }
}
