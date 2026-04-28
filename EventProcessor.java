package com.example.api;

public class EventProcessor {
    public void processEvent(String tenantId, EventPayload payload) {
        // ✅ Step 1: Validate required enablonTenantId
        if (tenantId == null || tenantId.isEmpty()) {
            throw new ValidationException("The EnablonTenantId field is required.");
        }
        
        // ✅ Step 2: Validate rootUrl format
        if (payload.getRootUrl() == null || !isValidUrl(payload.getRootUrl())) {
            throw new ValidationException("Invalid URL format for rootUrl.");
        }
        
        // ✅ Step 3: Validate aiServicesApiUrl is not empty
        if (payload.getAiServicesApiUrl() == null || payload.getAiServicesApiUrl().isEmpty()) {
            throw new ValidationException("The aiServicesApiUrl field is required and cannot be empty.");
        }
        
        // ✅ Step 4: Validate navigationAssistantStatus is boolean
        if (!(payload.getNavigationAssistantStatus() instanceof Boolean)) {
            throw new ValidationException("navigationAssistantStatus must be a boolean, not " + 
                payload.getNavigationAssistantStatus().getClass().getSimpleName());
        }
        
        // ✅ Event processing successful
        System.out.println("✅ Event validation passed. Processing event...");
    }

    private static boolean isValidUrl(String url) {
        try {
            new java.net.URL(url);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}