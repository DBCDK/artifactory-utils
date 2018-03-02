#!groovy

// Copyright Dansk Bibliotekscenter a/s. Licensed under GPLv3
// See license text at https://opensource.dbc.dk/licenses/gpl-3.0

import com.cloudbees.plugins.credentials.common.StandardUsernameCredentials
import com.cloudbees.plugins.credentials.CredentialsProvider
import groovy.json.JsonSlurper
import java.net.HttpURLConnection
import java.net.URL
import jenkins.model.Jenkins

def getCredentials = {description ->
    def credentials = CredentialsProvider.lookupCredentials(
        StandardUsernameCredentials.class, Jenkins.instance, null, null )

    return credentials.findResult {it.description == description ? it : null}
}

def splitReponame = {reponame ->
    def parts = reponame.split("/")
    def repoKey = parts[0].split("\\.")[0]
    return new Tuple(repoKey, parts[1])
}

def getTagsList = {baseUrl, repoKey, imagename, auth ->
    def url = String.format("%s/api/docker/%s/v2/%s/tags/list", baseUrl,
        repoKey, imagename)
    def connection = url.toURL().openConnection()
    connection.setRequestMethod("GET")
    connection.setRequestProperty("Authorization", auth)
    return connection.getInputStream().getText()
}

def parseJson = {json ->
    def jsonSlurper = new JsonSlurper()
    return jsonSlurper.parseText(json)
}

def main = {
    def baseUrl = "https://artifactory.dbc.dk/artifactory"
    def artifactoryLogin = "isworker login for artifactory"
    def tagPrefix = "DIT-"
    def reponame = "docker-io.dbc.dk/dbc-payara-flowstore"

    def c = getCredentials(artifactoryLogin)
    if(c == null) {
        return "counldn't get credentials"
    }

    def auth = String.format("%s:%s", c.username, c.password).bytes.encodeBase64().toString()
    def repoTuple = splitReponame(reponame)
    def json = parseJson(getTagsList(baseUrl, repoTuple.get(0),
        repoTuple.get(1), auth))
    def list = json.tags.findAll{it.startsWith(tagPrefix)}
    if(list.any{!it.isInteger()}) {
        // return list unsorted if not all values are integers
        return list
    }
    list = list.collect{Integer.valueOf(it.substring(tagPrefix.size()))}
        .sort{a, b -> b - a}.collect{it = tagPrefix + it}
    return list
}

return main()
