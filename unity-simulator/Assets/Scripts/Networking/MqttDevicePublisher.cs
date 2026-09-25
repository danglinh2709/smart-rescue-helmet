using System;
using System.Threading;
using System.Threading.Tasks;
using MQTTnet;
using MQTTnet.Client;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Networking
{
    public sealed class MqttDevicePublisher : MonoBehaviour, IDeviceTransport
    {
        [SerializeField] private bool publishEnabled = true;
        [SerializeField] private string host = "localhost";
        [SerializeField] private int port = 1883;
        public bool IsConnected { get; private set; }
        public event Action<string> ConnectionStateChanged;
        private IMqttClient _client;
        private float _nextRetry;
        private async void Start()
        {
            try { await ConnectAsync(host, port, CancellationToken.None); }
            catch { SetConnectionState(false); }
        }
        private void Update()
        {
            if (!publishEnabled || IsConnected || Time.unscaledTime < _nextRetry) return;
            _nextRetry = Time.unscaledTime + 3f;
            _ = ConnectAsync(host, port, CancellationToken.None);
        }
        public async Task ConnectAsync(string host, int port, CancellationToken cancellationToken)
        {
            _client = new MqttFactory().CreateMqttClient();
            _client.DisconnectedAsync += _ => { SetConnectionState(false); return Task.CompletedTask; };
            await _client.ConnectAsync(new MqttClientOptionsBuilder().WithTcpServer(host, port).Build(), cancellationToken);
            SetConnectionState(true);
        }
        public void SetPublishingEnabled(bool enabled)
        {
            publishEnabled = enabled;
            SetConnectionState(enabled && IsConnected);
        }
        public void SetConnectionState(bool connected)
        {
            if (IsConnected == connected) return;
            IsConnected = connected;
            ConnectionStateChanged?.Invoke(connected ? "CONNECTED" : "DISCONNECTED");
        }
        public Task<bool> PublishAsync(string topic, string payload, int qos, CancellationToken cancellationToken)
        {
            if (!publishEnabled || !IsConnected || cancellationToken.IsCancellationRequested) return Task.FromResult(false);
            return PublishConnectedAsync(topic, payload, qos, cancellationToken);
        }
        private async Task<bool> PublishConnectedAsync(string topic, string payload, int qos, CancellationToken token)
        {
            if (_client == null || !_client.IsConnected) return false;
            await _client.PublishAsync(new MqttApplicationMessageBuilder().WithTopic(topic).WithPayload(payload).WithQualityOfServiceLevel((MQTTnet.Protocol.MqttQualityOfServiceLevel)qos).Build(), token);
            return true;
        }
    }
}
