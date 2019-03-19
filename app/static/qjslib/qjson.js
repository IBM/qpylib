// Copyright 2019 IBM Corporation All Rights Reserved.
//
// SPDX-License-Identifier: Apache-2.0

function renderJsonContent(jsonTagId, targetDivTagId)
{
    var jsonTagContent = $("#" + jsonTagId).html();
    var json = JSON.parse(jsonTagContent);
    $("#" + targetDivTagId).append(renderJson(json));
}

function renderJson(json)
{
    if (json['@type'] === 'offense')
    {
        return renderOffense(json);
    }
    else if (json['@type'] === 'asset')
    {
        return renderAsset(json);
    }

    return 'Unknown JSON-LD type';
}

function renderOffense(json)
{
    return '<table><tbody>' +
        '<tr><td>Offense ID</td><td>' + json.data.id + '</td></tr>' +
        '<tr><td>Source IP</td><td>' + json.data.offense_source + '</td></tr>' +
        '<tr><td>Severity</td><td>' + json.data.severity + '</td></tr>' +
        '<tr><td>Status</td><td>' + json.data.status + '</td></tr>' +
        '</tbody></table>';
}

function renderAsset(json)
{
    var assetName = 'Unknown';
    var osID = 'Unknown';
    var propertiesLength = json.data.properties.length;

    for (var i = 0; i < propertiesLength; i++)
    {
        var property = json.data.properties[i];
        if (property.name === 'Primary OS ID')
        {
            osID = property.value;
        }
        else if (property.name === 'Given Name')
        {
            assetName = property.value;
        }
    }

    return ('<table><tbody>' +
            '<tr><td>Asset ID</td><td>' + json.data.id + '</td></tr>' +
            '<tr><td>Name</td><td>' + assetName + '</td></tr>' +
            '<tr><td>IP Address</td><td>' + json.data.interfaces[0].ip_addresses[0].value + '</td></tr>' +
            '<tr><td>OS ID</td><td>' + osID + '</td></tr>' +
            '</tbody></table>')
}
