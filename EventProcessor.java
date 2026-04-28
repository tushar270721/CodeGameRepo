package com.example.api;

public class EventProcessor {
    public void processEvent(String tenantId, EventPayload payload) {
        // Input validation
        if (tenantId == null || tenantId.isEmpty()) {
                throw new ValidationException("The EnablonTenantId field is required.");
        }
        if (!isValidUrl(payload.getRootUrl())) {
                throw new ValidationException("Invalid URL format for rootUrl.");
        }
        if (!(payload.getNavigationAssistantStatus() instanceof Boolean)) {
                throw new ValidationException("navigationAssistantStatus must be a boolean.");
        }

        // Process event
        System.out.println("Processing event...");
    }

        private static boolean isValidUrl(String url) {
                try {
                        new URL(url);
                        return true;
                } catch (Exception e) {
                        return false;
                }
        }
}