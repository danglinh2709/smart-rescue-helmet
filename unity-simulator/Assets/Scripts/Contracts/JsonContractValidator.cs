using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text.Json;
using UnityEngine;

namespace SmartRescueHelmet.Unity.Contracts
{
    public static class JsonContractValidator
    {
        public static bool IsValid(string schemaFileName, string json)
        {
            try
            {
                using (var schema = JsonDocument.Parse(File.ReadAllText(Path.Combine(Application.streamingAssetsPath, "contracts", schemaFileName))))
                using (var payload = JsonDocument.Parse(json))
                {
                    return Validate(schema.RootElement, payload.RootElement, schema.RootElement);
                }
            }
            catch (Exception exception) when (exception is JsonException || exception is IOException || exception is ArgumentException)
            {
                return false;
            }
        }

        private static bool Validate(JsonElement schema, JsonElement value, JsonElement root)
        {
            if (schema.TryGetProperty("$ref", out var reference))
            {
                var name = reference.GetString().Replace("#/$defs/", string.Empty);
                return Validate(root.GetProperty("$defs").GetProperty(name), value, root);
            }

            if (schema.TryGetProperty("anyOf", out var alternatives))
            {
                foreach (var option in alternatives.EnumerateArray())
                {
                    if (Validate(option, value, root)) return true;
                }
                return false;
            }

            if (schema.TryGetProperty("const", out var constant) && value.GetRawText() != constant.GetRawText()) return false;
            if (schema.TryGetProperty("enum", out var allowed) && !Contains(allowed, value)) return false;

            if (!schema.TryGetProperty("type", out var type)) return true;
            switch (type.GetString())
            {
                case "null": return value.ValueKind == JsonValueKind.Null;
                case "boolean": return value.ValueKind == JsonValueKind.True || value.ValueKind == JsonValueKind.False;
                case "number": return value.ValueKind == JsonValueKind.Number;
                case "integer": return value.ValueKind == JsonValueKind.Number && value.TryGetInt64(out _);
                case "string": return ValidateString(schema, value);
                case "object": return ValidateObject(schema, value, root);
                default: return false;
            }
        }

        private static bool ValidateString(JsonElement schema, JsonElement value)
        {
            if (value.ValueKind != JsonValueKind.String) return false;
            var text = value.GetString();
            if (schema.TryGetProperty("minLength", out var minimum) && text.Length < minimum.GetInt32()) return false;
            if (schema.TryGetProperty("maxLength", out var maximum) && text.Length > maximum.GetInt32()) return false;
            if (schema.TryGetProperty("format", out var format))
            {
                if (format.GetString() == "date-time" && !DateTimeOffset.TryParse(text, CultureInfo.InvariantCulture, DateTimeStyles.None, out _)) return false;
                if (format.GetString() == "uuid" && !Guid.TryParse(text, out _)) return false;
            }
            return true;
        }

        private static bool ValidateObject(JsonElement schema, JsonElement value, JsonElement root)
        {
            if (value.ValueKind != JsonValueKind.Object) return false;
            if (schema.TryGetProperty("required", out var required))
            {
                foreach (var property in required.EnumerateArray())
                {
                    if (!value.TryGetProperty(property.GetString(), out _)) return false;
                }
            }
            if (!schema.TryGetProperty("properties", out var properties)) return true;
            foreach (var property in value.EnumerateObject())
            {
                if (!properties.TryGetProperty(property.Name, out var propertySchema)) return false;
                if (!Validate(propertySchema, property.Value, root)) return false;
            }
            return true;
        }

        private static bool Contains(JsonElement allowed, JsonElement value)
        {
            foreach (var item in allowed.EnumerateArray()) if (item.GetRawText() == value.GetRawText()) return true;
            return false;
        }
    }
}
