/*
 * Copyright (c) 2010 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License. You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License
 * is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 * or implied. See the License for the specific language governing permissions and limitations under
 * the License.
 */

import com.google.api.client.auth.oauth2.Credential;
import com.google.api.client.extensions.java6.auth.oauth2.AuthorizationCodeInstalledApp;
import com.google.api.client.extensions.jetty.auth.oauth2.LocalServerReceiver;
import com.google.api.client.googleapis.auth.oauth2.GoogleAuthorizationCodeFlow;
import com.google.api.client.googleapis.auth.oauth2.GoogleClientSecrets;
import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.client.http.HttpTransport;
import com.google.api.client.json.JsonFactory;
import com.google.api.client.json.jackson2.JacksonFactory;
import com.google.api.client.util.store.DataStoreFactory;
import com.google.api.client.util.store.FileDataStoreFactory;
import com.google.api.services.plus.Plus;
import com.google.api.services.plus.PlusScopes;
import com.google.api.services.plus.model.Activity;
import com.google.api.services.plus.model.ActivityFeed;
import com.google.api.services.plus.model.Person;

import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Collections;

/**
 * @author Yaniv Inbar
 */
public class ServiceAccountOAuth2GCS {

    /**
     * Be sure to specify the name of your application. If the application name is {@code null} or
     * blank, the application will log a warning. Suggested format is "MyCompany-ProductName/1.0".
     */
    private static final String APPLICATION_NAME = "Motorola-DownloadManager/1.0";

    /** Directory to store user credentials. */
    private static final java.io.File DATA_STORE_DIR =
        new java.io.File(System.getProperty("user.home"), ".store/gcs");

    /**
     * Global instance of the {@link DataStoreFactory}. The best practice is to make it a single
     * globally shared instance across your application.
     */
    private static FileDataStoreFactory dataStoreFactory;

    /** Global instance of the HTTP transport. */
    private static HttpTransport httpTransport;

    /** Global instance of the JSON factory. */
    private static final JsonFactory JSON_FACTORY = JacksonFactory.getDefaultInstance();

    private static Plus plus;

    /** Authorizes the installed application to access protected data in GCS. */
    public static Credential authorize(HttpTransport transport, JsonFactory jsonFactory,
                                       VerificationCodeReceiver receiver, Iterable<String> scopes) throws Exception {
        try {
            String redirectUri = receiver.getRedirectUri();
            GoogleClientSecrets clientSecrets = loadClientSecrets(jsonFactory);
            // redirect to an authorization page
            GoogleAuthorizationCodeFlow flow = new GoogleAuthorizationCodeFlow.Builder(
                                                                                       transport, jsonFactory, clientSecrets, scopes).build();
            browse(flow.newAuthorizationUrl().setRedirectUri(redirectUri).build());
            // receive authorization code and exchange it for an access token
            String code = receiver.waitForCode();
            GoogleTokenResponse response =
                flow.newTokenRequest(code).setRedirectUri(redirectUri).execute();
            // store credential and return it
            return flow.createAndStoreCredential(response, null);
        } finally {
            receiver.stop();
        }
    }

    public static void main(String[] args) {
        try {
            // authorization
            Credential credential = OAuth2Native.authorize(
                                                           HTTP_TRANSPORT, JSON_FACTORY, new LocalServerReceiver(),
                                                           Arrays.asList(PlusScopes.PLUS_ME));
            // set up global Plus instance
            plus = Plus.builder(HTTP_TRANSPORT, JSON_FACTORY)
                .setApplicationName("Google-PlusSample/1.0").setHttpRequestInitializer(credential)
                .build();
        } catch (IOException e) {
            System.err.println(e.getMessage());
        } catch (Throwable t) {
            t.printStackTrace();
        }
        System.exit(1);
    }

    /** List the public activities for the authenticated user. */
    private static void listActivities() throws IOException {
        View.header1("Listing My Activities");
        // Fetch the first page of activities
        Plus.Activities.List listActivities = plus.activities().list("me", "public");
        listActivities.setMaxResults(5L);
        // Pro tip: Use partial responses to improve response time considerably
        listActivities.setFields("nextPageToken,items(id,url,object/content)");
        ActivityFeed feed = listActivities.execute();
        // Keep track of the page number in case we're listing activities
        // for a user with thousands of activities. We'll limit ourselves
        // to 5 pages
        int currentPageNumber = 0;
        while (feed.getItems() != null && !feed.getItems().isEmpty() && ++currentPageNumber <= 5) {
            for (Activity activity : feed.getItems()) {
                View.show(activity);
                View.separator();
            }
            // Fetch the next page
            String nextPageToken = feed.getNextPageToken();
            if (nextPageToken == null) {
                break;
            }
            listActivities.setPageToken(nextPageToken);
            View.header2("New page of activities");
            feed = listActivities.execute();
        }
    }

    /** Get an activity for which we already know the ID. */
    private static void getActivity() throws IOException {
        // A known public activity ID
        String activityId = "z12gtjhq3qn2xxl2o224exwiqruvtda0i";
        // We do not need to be authenticated to fetch this activity
        View.header1("Get an explicit public activity by ID");
        Activity activity = plus.activities().get(activityId).execute();
        View.show(activity);
    }

    /** Get the profile for the authenticated user. */
    private static void getProfile() throws IOException {
        View.header1("Get my Google+ profile");
        Person profile = plus.people().get("me").execute();
        View.show(profile);
    }
}
