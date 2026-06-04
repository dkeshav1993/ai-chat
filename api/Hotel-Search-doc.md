BASE URL - https://travelonedev-services.thomascook.in/

Token API -

End point -

POST https://travelonedev-services.thomascook.in/authenticationserver/authenticationService/generateToken

Request -

{
    "moduleID": "Traversia",
    "userName": "traversia",
    "password": "Traversia@123"
}

Response -

{
    "token": "v2.local.0OBP3q5P4OXIPdstdl89H73tGBwju0i4JHGJTG1Gho8aTucMFQiyWCzrhS4Y7LbzWd9waIqV6DQjywT8xKuwFZ4d0JSF6NoGAiq20NcyMW_KPIk7oyHv8TL8xnMH5FW9ItZfW6RmSwVqMxgUaI499uKmoXIup3YLbQ5Oajp7y5IFnvF6d_6KbK2Khx5Ir1eMGhyxU8_aER3ncOXYEyojyN5KMFq0XVcohR-7sieVgNz7tb75kg9X4TvGZG_B716rk80ZccBMIaDzQEOF9b_veuNAYFjevxn0a0OfVEIAH-RMgKfLz0jAK3Ip3rB8Lfx_wN1SpuVn9Mcy9iPbhJLRDNknnRjL5zBH3CaGcn9d6-NgX6DXK2RM1KclozHaJ-yprg3nQOAdB5YfFTmDlr6brYwrx6JdROJNOiWiBLmjGsscRGXVjDsJqEcB7fR8GW8wnPMbsTItlBj1kNCake1F5rU2ETZ43MamZ-Iy0-WTYtdsdABo5sLUD5Z5f2yR9lVXAWpRRTIeu8NH398Ezrkd073FAAxmgw2YUFzK9g2-cSgm8fzKPh-_NynQgbnvgo2PCqT03r8MWuCk1uc5WnEoI4uhsGIRZrty2uMoIblhq1GUOq5jVW_87sUNHfhovyecZ_bF9V41VOjd7Z2-CS4oRkYZZgTf_Gi2WsU_4N0fchbltvAVu86pEdg_L3vYZAvBX3VUTsnnY4SxNXeJJFJQIZv3tA8UHpHRki9ZfP_JEnI_HkO5TMQ9Okx-Ir4PshBgrz18uuEUoPuYa_LKsuuB_a20vTStt_gSUyjyZEAvnmFBzmdaWAYsJ3bovCm4QUhMWlGCCQVXjMJRJKRW-7cxDiIv3EcGqyqaGMHn2lFzJE8mGizbaIwI8P0AtLMnGKP-8vqbyR0lG4WDWCGZG0IYtWnfT-btxOYMXhb7pwwPvwErnk_uz6WSvlDEFVfAvVPacQRNcQes0BZ_8yiGTV430sG0-5RTsc6McQCuh0jt1w_KYUCWJXQ8QahykS1GipElOj1u78A2u5fIEsPxPffXnnkC",
    "correleationId": "Traversia-traversia-736ecd10-ba83-4b09-b070-7121d90a0bbf",
    "message": "Token Creation Is Sucessful",
    "tokenClaims": null,
    "tokenValid": true
}

============================================================================================

Above token to be passed in the header as bearer token. Remember, if we get token expired message from any below API, call above api again and reinstantiate the token

1) Auto Suggest API
Endpoint
POST /api/v1/landing/fetchAutoSuggest
		Request Body
		{
			"autoSuggestKey": "new de"
		}
		Success Response
		{
	"success": true,
	"status": 0,
	"message": "Suggestions fetched successfully",
	"autoSuggestId": "9b538e0c-8274-4792-aba4-0f2979ce5628",
	"autoSuggests": [
		{
			"uniqueId": "40262217",
			"type": "hotels",
			"name": "New Deal - APT with Terrace & Jacuzzi",
			"cityName": "Palmanova",
			"stateName": "Ud",
			"countryName": "Italy"
		},
		{
			"uniqueId": "15493123",
			"type": "locations",
			"name": "New Delhi",
			"cityName": "New Delhi",
			"stateName": "National Capital Territory Of Delhi",
			"countryName": "India"
		},
		{
			"uniqueId": "16992764",
			"type": "cities",
			"name": "New Deer",
			"cityName": "New Deer",
			"stateName": "Scotland",
			"countryName": "United Kingdom"
		},
		{
			"uniqueId": "687f69a73c00f2ee2675de04",
			"type": "pointOfInterest",
			"name": "New Delhi City Center Mall",
			"cityName": "New Delhi",
			"stateName": "Delhi N.C.R",
			"countryName": "India"
		},
		{
			"uniqueId": "16992764|HotelModel",
			"type": "airports",
			"name": "Aberdeen International Airport(ABZ)",
			"cityName": "New Deer",
			"stateName": "",
			"countryName": "United Kingdom"
		}
	]
}
		No Result Response
		{
		  "success": false,
		  "status": 500,
		  "message": "autosuggest returned no matching suggestions",
		  "apiPath": "uri=/api/v1/landing/fetchAutoSuggest",
		  "errorTime": "2026-05-22T12:14:47.083593092"
		}
		Downstream Null Response
		{
		  "success": false,
		  "status": 500,
		  "message": "downstream returned null response",
		  "apiPath": "uri=/api/v1/landing/fetchAutoSuggest",
		  "errorTime": "2026-05-22T12:14:47.083593092"
		}

		Request Body
		{
		  "autoSuggestKey": null
		}
		Validation Error - Missing autoSuggestKey
		{
		  "success": false,
		  "status": 400,
		  "message": "autoSuggestKey must not be null",
		  "apiPath": "uri=/api/v1/landing/fetchAutoSuggest",
		  "errorTime": "2026-05-22T12:14:47.083593092"
		}

================================================================================

2) Search API 

Endpoint
POST /api/v1/api/v1/wrapper/hotels/search
Request Body ->
{
  "autoSuggestId": "321f5a32-9b8b-4a72-b84c-da13a613da8f",
  "autosuggestIdentifier": {
    "cityName": "New Delhi",
    "countryName": "India",
    "name": "New Delhi",
    "stateName": "National Capital Territory Of Delhi",
    "type": "locations",
    "uniqueIdentifier": "15493123"
  },
  "checkIn": "2026-06-09",
  "checkOut": "2026-06-10",
  "journeyType": "Domestic",
  "pageIndex": null,
  "pageSize": null,
  "rooms": [
    {
      "adultCount": 1,
      "childrenCount": 0,
      "guests": [
        {
          "city": "Mumbai",
          "country": "India",
          "dateOfBirth": "02-12-1993",
          "email": "keshav.dutta@thomascook.in",
          "employeeCode": "63228",
          "firstName": "Keshav",
          "guestType": "ADT",
          "lastName": "Dutta",
          "mobileNo": "9560675459",
          "state": "Maharashtra",
          "title": "Mr",
          "travellerId": 363
        }
      ],
      "roomNo": 1
    }
  ],
  "travelType": "Business Travel"
}
1. success response 
 {
  "success": true,
  "message": "Search results retrieved successfully",
  "status": 0,
  "data": {
    "searchKey": "12fd7691-a190-42da-a8dc-18631a482d18",
    "autoSuggestId": "321f5a32-9b8b-4a72-b84c-da13a613da8f",
    "page": 1,
    "limit": 25,
    "minRate": null,
    "maxRate": null,
    "minStarRating": 3,
    "maxStarRating": 5,
    "cacheKey": "0c75883f-4b0d-488c-bd33-98f148bcd87a",
    "vervotechHotelCount": 50,
    "hotels": [
      {
        "vervotechHotelId": "39759509",
        "providerInfo": [
          {
            "vendorName": "GRNConnect",
            "providerHotelCode": "1395928",
            "fareType": "MARKETFARE",
            "totalFare": 5263,
            "baseFare": 4278.35,
            "taxes": 150.17,
            "additionalCharges": 834.48,
            "refundable": true,
            "boardBasis": [],
            "inPolicy": null,
            "outPolicyReasons": [],
            "paymentType": "prepaid",
            "ruleName": null,
            "outPolicyReasonKey": []
          }
        ],
        "name": "Deventure Sarovar Portico Kapashera",
        "brandName": null,
        "chainName": null,
        "heroImage": "https://i.travelapi.com/lodging/18000000/17190000/17184300/17184235/w1600h1527x0y4-da00fd23_z.jpg",
        "images": [
          {
            "caption": "Primary image",
            "category": null,
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/18000000/17190000/17184300/17184235/w1600h1527x0y4-da00fd23_b.jpg",
                "href": null,
                "links": null
              }
            ],
            "roomId": null
          },
          {
            "caption": "Lobby",
            "category": null,
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/18000000/17190000/17184300/17184235/42432dac_b.jpg",
                "href": null,
                "links": null
              }
            ],
            "roomId": null
          },
          {
            "caption": "Reception",
            "category": null,
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/18000000/17190000/17184300/17184235/201c3b48_b.jpg",
                "href": null,
                "links": null
              }
            ],
            "roomId": null
          },
          {
            "caption": "Room",
            "category": null,
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/18000000/17190000/17184300/17184235/2f994726_b.jpg",
                "href": null,
                "links": null
              }
            ],
            "roomId": null
          },
          {
            "caption": "Room",
            "category": null,
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/18000000/17190000/17184300/17184235/6ec2d219_b.jpg",
                "href": null,
                "links": null
              }
            ],
            "roomId": null
          }
        ],
        "starRating": "4",
        "fareType": [
          "MARKETFARE"
        ],
        "isTCRecommended": true,
        "overallMinRate": null,
        "overallMaxRate": null,
        "facilities": [
          {
            "id": "2070",
            "groupId": "12",
            "groupName": "Laundry Services",
            "name": "Dry cleaning/laundry service",
            "link": ""
          },
          {
            "id": "1073744111",
            "groupId": "29",
            "groupName": "Banquet",
            "name": "Banquet hall",
            "link": ""
          },
          {
            "id": "2131",
            "groupId": "6",
            "groupName": "Business Center",
            "name": "Meeting rooms",
            "link": ""
          },
          {
            "id": "2390",
            "groupId": "16",
            "groupName": "Internet",
            "name": "Free WiFi",
            "link": ""
          },
          {
            "id": "1073744740",
            "groupId": "64",
            "groupName": "Wheelchair accessible",
            "name": "Wheelchair accessible – no",
            "link": ""
          }
        ],
        "currency": "INR",
        "propertyType": "Hotel",
        "contact": {
          "address": {
            "line1": "88-89 Bijwasan Road, Kapashera",
            "line2": null,
            "city": "New Delhi",
            "code": "DEL",
            "destinationCode": null,
            "state": "Delhi N.C.R.",
            "stateCode": "DL",
            "country": "India",
            "countryCode": "IN",
            "postalCode": "110037"
          },
          "phones": null
        }
      }
    ],
    "inprogress": true
  }
}

2. If these 2 parameters are not coming as it is in the response that means, its an error case => "success": true, "status": 0,

================================================================================

3) Background Processing API
Endpoint
POST /api/v1/hotels/backgroundProcessStatus
		Request Body
		{
      "autoSuggestId": "321f5a32-9b8b-4a72-b84c-da13a613da8f",
      "cacheKey": "0c75883f-4b0d-488c-bd33-98f148bcd87a",
      "searchKey": "12fd7691-a190-42da-a8dc-18631a482d18"
    }

  Note - 
  1. AutosuggestId is the one coming from autosuggest API, similarly search keys are the one from hotels/search API

  2. This API needs to be polled every 1 second. If the API response "inProgress": false, this means, polling in the backend done. Remember, first hotels/search API returns list of hotels, we will display it to the customer. If customer needs more hotels, we will keep calling this background check API, till we get "inProgress": false. Post this flag as false, we will call hotels/search-by-poll API.


1. 	Success Response
		{
      "success": true,
      "status": 0,
      "message": "Background process status fetched successfully.",
      "data": {
        "status": 200,
        "inProgress": false,
        "cacheKey": "0c75883f-4b0d-488c-bd33-98f148bcd87a"
  }
}
2. Response indicates processing is going on
{
	"success": true,
	"status": 0,
	"message": "Background process status fetched successfully.",
	"data": {
		"status": 200,
		"inProgress": true,
		"cacheKey": "0c75883f-4b0d-488c-bd33-98f148bcd87a"
	}
}

		
3. Generic Internal Server Error
		{
		  "success": false,
		  "status": 500,
		  "message": "Internal server error",
		  "apiPath": "uri=/api/v1/wrapper/hotels/background-status",
		  "errorTime": "2026-05-22T15:20:10.123456789"
		}

================================================================================

4) Search by poll API Documentation - 

endpoint - /api/v1/hotels/search-by-poll

request - {
	"autoSuggestId": "321f5a32-9b8b-4a72-b84c-da13a613da8f",
	"cacheKey": "0c75883f-4b0d-488c-bd33-98f148bcd87a",
	"capping_reached": false,
	"checkIn": "2026-06-09",
	"checkOut": "2026-06-10",
	"hotelReceived": 0,
	"isSearchResultsProcessed": true,
	"pageIndex": 1,
	"pageSize": 300,
	"searchKey": "12fd7691-a190-42da-a8dc-18631a482d18"
}
response (Count is 300 in this case, we can call this API again if the received hotel feed is greater than or equal to asked page size. In case receieved feed is less than asked, this means no more hotel available. Response structure is same as the hotels/search API for easy mapping. board basis inside providerInfo is the one to check for "Breakfast". If empty, means no meals. Consider price breakup, policy information from providerInfo only. Scan rest) - 
{
  "success": true,
  "message": "Search results retrieved from cache successfully",
  "status": 0,
  "data": {
    "searchKey": "12fd7691-a190-42da-a8dc-18631a482d18",
    "autoSuggestId": "321f5a32-9b8b-4a72-b84c-da13a613da8f",
    "page": 1,
    "limit": 300,
    "minRate": null,
    "maxRate": null,
    "minStarRating": 2,
    "maxStarRating": 4,
    "cacheKey": "0c75883f-4b0d-488c-bd33-98f148bcd87a",
    "vervotechHotelCount": 4003,
    "hotels": [
      {
        "vervotechHotelId": "16354408",
        "providerInfo": [
          {
            "vendorName": "GRNConnect",
            "providerHotelCode": "2050512",
            "fareType": "MARKETFARE",
            "totalFare": 513,
            "baseFare": 416.27,
            "taxes": 14.61,
            "additionalCharges": 82.12,
            "refundable": true,
            "boardBasis": [],
            "inPolicy": null,
            "outPolicyReasons": [],
            "paymentType": "prepaid",
            "ruleName": null,
            "outPolicyReasonKey": []
          }
        ],
        "name": "Bunk Hostel Delhi",
        "brandName": null,
        "chainName": null,
        "heroImage": "",
        "images": [
          {
            "caption": "Lobby",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/40000000/39530000/39523300/39523289/4f6ab6c1_b.jpg",
                "href": "",
                "links": []
              }
            ],
            "roomId": []
          },
          {
            "caption": "Lobby",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/40000000/39530000/39523300/39523289/181fd768_b.jpg",
                "href": "",
                "links": []
              }
            ],
            "roomId": []
          },
          {
            "caption": "Lobby",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/40000000/39530000/39523300/39523289/5423fba9_b.jpg",
                "href": "",
                "links": []
              }
            ],
            "roomId": []
          },
          {
            "caption": "Lobby",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/40000000/39530000/39523300/39523289/2fcec290_b.jpg",
                "href": "",
                "links": []
              }
            ],
            "roomId": []
          },
          {
            "caption": "Reception",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/40000000/39530000/39523300/39523289/df08c636_b.jpg",
                "href": "",
                "links": []
              }
            ],
            "roomId": []
          }
        ],
        "starRating": "2",
        "fareType": [
          "MARKETFARE"
        ],
        "isTCRecommended": true,
        "overallMinRate": null,
        "overallMaxRate": null,
        "facilities": [
          {
            "id": "369",
            "groupId": "12",
            "groupName": "Laundry Services",
            "name": "Laundry facilities",
            "link": ""
          },
          {
            "id": "4003",
            "groupId": "80",
            "groupName": "Conveniences",
            "name": "Luggage storage",
            "link": "http://98.70.9.148:8881/assests/public-relation.png"
          },
          {
            "id": "1073743884",
            "groupId": "32",
            "groupName": "Safe deposit box",
            "name": "Lockers available",
            "link": ""
          },
          {
            "id": "3861",
            "groupId": "1",
            "groupName": "Parking",
            "name": "Free self parking",
            "link": "http://98.70.9.148:8881/assests/public-relation.png"
          },
          {
            "id": "4006",
            "groupId": "18",
            "groupName": "Airport Shuttle",
            "name": "Airport transportation - pickup (surcharge)",
            "link": ""
          }
        ],
        "currency": "INR",
        "propertyType": "Hostel",
        "contact": {
          "address": {
            "line1": "22/1 Main Bazar Rd",
            "line2": null,
            "city": "New Delhi",
            "code": "DEL",
            "destinationCode": null,
            "state": "Dl",
            "stateCode": "DL",
            "country": "India",
            "countryCode": "IN",
            "postalCode": "110055"
          },
          "phones": [
            "91 9899877102"
          ]
        }
      },
      {
        "vervotechHotelId": "39647288",
        "providerInfo": [
          {
            "vendorName": "GRNConnect",
            "providerHotelCode": "1393737",
            "fareType": "MARKETFARE",
            "totalFare": 704,
            "baseFare": 571.51,
            "taxes": 20.06,
            "additionalCharges": 112.43,
            "refundable": true,
            "boardBasis": [],
            "inPolicy": null,
            "outPolicyReasons": [],
            "paymentType": "prepaid",
            "ruleName": null,
            "outPolicyReasonKey": []
          }
        ],
        "name": "Airport Hotel Mayank Residency",
        "brandName": null,
        "chainName": null,
        "heroImage": "https://www.tboholidays.com//imageresource.aspx?img=FbrGPTrju5e5v0qrAGTD8pPBsj8/wYA5F3wAmN3NGLWIJlk/wUEUZy9wh3kSLLX5jx4cNBV+wcD6Kmw28m4NPBYvbv00YaktkINb4OzEgaw=",
        "images": [
          {
            "caption": "",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://www.tboholidays.com//imageresource.aspx?img=FbrGPTrju5e5v0qrAGTD8pPBsj8/wYA5F3wAmN3NGLWIJlk/wUEUZy9wh3kSLLX5jx4cNBV+wcD6Kmw28m4NPBYvbv00YaktkINb4OzEgaw=",
                "href": "",
                "links": []
              }
            ],
            "roomId": []
          },
          {
            "caption": "",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://www.tboholidays.com//imageresource.aspx?img=FbrGPTrju5e5v0qrAGTD8pPBsj8/wYA5F3wAmN3NGLWIJlk/wUEUZy9wh3kSLLX5jx4cNBV+wcD6Kmw28m4NPBDOsyiH18ZKuVXjekFUZGM=",
                "href": "",
                "links": []
              }
            ],
            "roomId": []
          },
          {
            "caption": "",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://www.tboholidays.com//imageresource.aspx?img=FbrGPTrju5e5v0qrAGTD8pPBsj8/wYA5F3wAmN3NGLWIJlk/wUEUZy9wh3kSLLX5jx4cNBV+wcD6Kmw28m4NPApvlTklZgR29bom9h9OwBU=",
                "href": "",
                "links": []
              }
            ],
            "roomId": []
          },
          {
            "caption": "",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://www.tboholidays.com//imageresource.aspx?img=FbrGPTrju5e5v0qrAGTD8pPBsj8/wYA5F3wAmN3NGLWIJlk/wUEUZy9wh3kSLLX5jx4cNBV+wcD6Kmw28m4NPK+FzAUrEXNHAZ3MTGHu9CU=",
                "href": "",
                "links": []
              }
            ],
            "roomId": []
          },
          {
            "caption": "",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://www.tboholidays.com//imageresource.aspx?img=FbrGPTrju5e5v0qrAGTD8pPBsj8/wYA5F3wAmN3NGLWIJlk/wUEUZy9wh3kSLLX5jx4cNBV+wcD6Kmw28m4NPKzKNOmGdo+vZDQww0/Y9g4=",
                "href": "",
                "links": []
              }
            ],
            "roomId": []
          }
        ],
        "starRating": "3",
        "fareType": [
          "MARKETFARE"
        ],
        "isTCRecommended": true,
        "overallMinRate": null,
        "overallMaxRate": null,
        "facilities": [
          {
            "id": "4",
            "groupId": "74",
            "groupName": "Transportation",
            "name": "Shopping center shuttle (surcharge)",
            "link": ""
          },
          {
            "id": "5",
            "groupId": "74",
            "groupName": "Transportation",
            "name": "Area shuttle (surcharge)",
            "link": ""
          },
          {
            "id": "6",
            "groupId": "18",
            "groupName": "Airport Shuttle",
            "name": "Airport transportation (surcharge)",
            "link": ""
          },
          {
            "id": "7",
            "groupId": "14",
            "groupName": "Restaurant",
            "name": "Couples/private dining",
            "link": ""
          },
          {
            "id": "8",
            "groupId": "64",
            "groupName": "Wheelchair accessible",
            "name": "Wheelchair accessible – no",
            "link": ""
          }
        ],
        "currency": "INR",
        "propertyType": "Hotel",
        "contact": {
          "address": {
            "line1": "A-230, Road no. 2, Mahipalpur Extension, 110037 New Delhi, India",
            "line2": null,
            "city": "New Delhi",
            "code": "DEL",
            "destinationCode": null,
            "state": "Delhi",
            "stateCode": "DL",
            "country": "India",
            "countryCode": "IN",
            "postalCode": "110037"
          },
          "phones": [
            "919999874162",
            "91 11 42198562",
            "9999874162"
          ]
        }
      },
      {
        "vervotechHotelId": "70447659",
        "providerInfo": [
          {
            "vendorName": "GRNConnect",
            "providerHotelCode": "1394691",
            "fareType": "MARKETFARE",
            "totalFare": 1818,
            "baseFare": 1477.21,
            "taxes": 51.85,
            "additionalCharges": 288.94,
            "refundable": false,
            "boardBasis": [],
            "inPolicy": null,
            "outPolicyReasons": [],
            "paymentType": "prepaid",
            "ruleName": null,
            "outPolicyReasonKey": []
          }
        ],
        "name": "Hotel Mourya Deluxe",
        "brandName": null,
        "chainName": null,
        "heroImage": "https://i.travelapi.com/lodging/105000000/104510000/104505300/104505257/f640e886_z.jpg",
        "images": [
          {
            "caption": "Primary image",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/105000000/104510000/104505300/104505257/f640e886_b.jpg",
                "href": "",
                "links": []
              }
            ],
            "roomId": [
              "324669957"
            ]
          },
          {
            "caption": "Lobby",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/105000000/104510000/104505300/104505257/9ce23188_b.jpg",
                "href": "",
                "links": []
              }
            ],
            "roomId": []
          },
          {
            "caption": "Reception",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/105000000/104510000/104505300/104505257/3d66b735_b.jpg",
                "href": "",
                "links": []
              }
            ],
            "roomId": []
          },
          {
            "caption": "Room",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/105000000/104510000/104505300/104505257/068ad095_b.jpg",
                "href": "",
                "links": []
              }
            ],
            "roomId": [
              "324669957"
            ]
          },
          {
            "caption": "Room",
            "category": "",
            "links": [
              {
                "size": "Standard",
                "providerHref": "https://i.travelapi.com/lodging/105000000/104510000/104505300/104505257/337ec6b5_b.jpg",
                "href": "",
                "links": []
              }
            ],
            "roomId": [
              "324669957"
            ]
          }
        ],
        "starRating": "3",
        "fareType": [
          "MARKETFARE"
        ],
        "isTCRecommended": true,
        "overallMinRate": null,
        "overallMaxRate": null,
        "facilities": [
          {
            "id": "2537",
            "groupId": "14",
            "groupName": "Restaurant",
            "name": "Number of restaurants - 1",
            "link": ""
          },
          {
            "id": "2137",
            "groupId": "10",
            "groupName": "Non Smoking",
            "name": "Smoke-free property",
            "link": ""
          },
          {
            "id": "1073744740",
            "groupId": "64",
            "groupName": "Wheelchair accessible",
            "name": "Wheelchair accessible – no",
            "link": ""
          },
          {
            "id": "2043",
            "groupId": "35",
            "groupName": "Multilingual",
            "name": "Multilingual staff",
            "link": ""
          },
          {
            "id": "2063",
            "groupId": "80",
            "groupName": "Conveniences",
            "name": "24-hour front desk",
            "link": "http://98.70.9.148:8881/assests/public-relation.png"
          }
        ],
        "currency": "INR",
        "propertyType": "Hotel",
        "contact": {
          "address": {
            "line1": "9921-23-Gali No. 5, Multani Dhanda",
            "line2": null,
            "city": "New Delhi",
            "code": "DEL",
            "destinationCode": null,
            "state": "Delhi",
            "stateCode": "DL",
            "country": "India",
            "countryCode": "IN",
            "postalCode": "110055"
          },
          "phones": [
            "91 11 3594 8832"
          ]
        }
      }
    ],
    "inprogress": false
  }
}
2. Failed case -

No Result Response
		{
		  "success": false,
		  "status": 500,
		  "message": "autosuggest returned no matching suggestions",
		  "apiPath": "uri=/api/v1/landing/fetchAutoSuggest",
		  "errorTime": "2026-05-22T12:14:47.083593092"
		}

================================================================================

5) hotel details documentation  - 

endpoint - api/v1/room/getHotelDetails

request -
{
	"hotelId": "16282095",
	"searchKey": "12fd7691-a190-42da-a8dc-18631a482d18"
}

response( This API is the static dump of the hotels. It contains complete hotel information) - 
{
	"success": true,
	"status": 0,
	"message": "Hotel details fetched successfully",
	"searchKey": "12fd7691-a190-42da-a8dc-18631a482d18",
	"hotelData": {
		"_id": "685d454c0483d9af784fd7ad",
		"isTCRecommended": false,
		"fareType": "",
		"paymentType": "",
		"name": "Hotel Shree Sai Dham Near New Delhi Railway Station, Paharganj",
		"brandName": "",
		"chainName": "",
		"rating": "3",
		"categoryName": "",
		"description": "This hotel has 3 floors in 1 building and offers designated smoking areas., Take advantage of the hotel's 24-hour room service., Featured amenities include a 24-hour front desk, luggage storage, and a safe deposit box at the front desk. Free self parking is available onsite., Make yourself at home in one of the 24 air-conditioned guestrooms. Complimentary wireless internet access is available to keep you connected. Private bathrooms with showers feature rainfall showerheads and complimentary toiletries. Conveniences include safes and desks, and housekeeping is provided daily., Distances are displayed to the nearest 0.1 mile and kilometer. <br /> <p>Kasturba Gandhi Marg - 0.5 km / 0.3 mi <br /> FICCI Auditorium - 0.7 km / 0.5 mi <br /> Max Mueller Bhawan - 1 km / 0.6 mi <br /> Palika Bazaar - 1.1 km / 0.7 mi <br /> Western Court Building - 1.4 km / 0.8 mi <br /> Jantar Mantar - 1.8 km / 1.1 mi <br /> Supreme Court - 2 km / 1.2 mi <br /> Pragati Maidan - 2.5 km / 1.5 mi <br /> India Gate - 2.5 km / 1.6 mi <br /> Gurudwara Bangla Sahib - 2.7 km / 1.7 mi <br /> Gole Market - 2.7 km / 1.7 mi <br /> National Museum - 2.9 km / 1.8 mi <br /> Jama Masjid - 3 km / 1.9 mi <br /> Delhi High Court - 3 km / 1.9 mi <br /> Vigyan Bhavan - 3.2 km / 2 mi <br /> </p><p>The preferred airport for Hotel Shree Sai Dham Near New Delhi Railway Station, Paharganj is Indira Gandhi International Airport (DEL) - 20.2 km / 12.5 mi </p>, With a stay at Hotel Shree Sai Dham Near New Delhi Railway Station, Paharganj in New Delhi (Chanakyapuri), you'll be within a 5-minute drive of Gurudwara Bangla Sahib and India Gate.  This hotel is 2.4 mi (3.9 km) from Chandni Chowk and 5.3 mi (8.6 km) from Swaminarayan Akshardham Temple., In New Delhi (Chanakyapuri), Hindi, English, Debit cards not accepted, Cash",
		"facilities": [
			{
				"id": "1073745352",
				"groupId": "62",
				"groupName": "Elevator",
				"name": "Elevator door width (inches) - 36",
				"link": ""
			},
			{
				"id": "1073744430",
				"groupId": "34",
				"groupName": "Disable Friendly",
				"name": "Wheelchair accessible (may have limitations)",
				"link": ""
			},
			{
				"id": "2016",
				"groupId": "32",
				"groupName": "Safe deposit box",
				"name": "Safe-deposit box at front desk",
				"link": ""
			},
			{
				"id": "1073745353",
				"groupId": "62",
				"groupName": "Elevator",
				"name": "Elevator door width (centimeters) - 91",
				"link": ""
			},
			{
				"id": "1073745332",
				"groupId": "74",
				"groupName": "Transportation",
				"name": "No accessible shuttle",
				"link": ""
			},
			{
				"id": "4003",
				"groupId": "80",
				"groupName": "Conveniences",
				"name": "Luggage storage",
				"link": "http://98.70.9.148:8881/assests/public-relation.png"
			},
			{
				"id": "3861",
				"groupId": "1",
				"groupName": "Parking",
				"name": "Free self parking",
				"link": "http://98.70.9.148:8881/assests/public-relation.png"
			},
			{
				"id": "8",
				"groupId": "62",
				"groupName": "Elevator",
				"name": "Elevator",
				"link": ""
			},
			{
				"id": "2063",
				"groupId": "80",
				"groupName": "Conveniences",
				"name": "24-hour front desk",
				"link": "http://98.70.9.148:8881/assests/public-relation.png"
			},
			{
				"id": "2390",
				"groupId": "16",
				"groupName": "Internet",
				"name": "Free WiFi",
				"link": ""
			}
		],
		"policies": [
			{
				"text": "  No pets and no service animals are allowed at this property.  ",
				"title": "know_before_you_go"
			}
		],
		"propertyType": "Hotel",
		"contact": {
			"address": {
				"line1": "3228, School Lane",
				"line2": "",
				"city": "New Delhi",
				"code": "DEL",
				"destinationCode": "",
				"state": "New Delhi",
				"stateCode": "DL",
				"country": "India",
				"countryCode": "IN",
				"postalCode": "110055"
			},
			"phones": [
				"91 8447685460"
			]
		},
		"hotelId": "16282095",
		"resultIndex": "",
		"heroImage": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/fccc6ac0_z.jpg",
		"checkin": {
			"date": "",
			"time": "12:00 PM",
			"instructions": "<ul>  <li>Extra-person charges may apply and vary depending on property policy</li><li>Government-issued photo identification and a credit card, debit card, or cash deposit may be required at check-in for incidental charges</li><li>Special requests are subject to availability upon check-in and may incur additional charges; special requests cannot be guaranteed</li><li>This property accepts cash</li>  </ul>",
			"specialInstruction": ""
		},
		"checkout": {
			"date": "",
			"time": "12:00 PM"
		},
		"images": {
			"isDummy": true,
			"data": [
				{
					"caption": "Primary image",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/fccc6ac0_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/fccc6ac0_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325193197"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c393849c_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c393849c_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325193197"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a9e29d4e_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a9e29d4e_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325193197"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/1e8105cf_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/1e8105cf_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325193197"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a3c98683_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a3c98683_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325193197"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/9ff01583_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/9ff01583_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325410506"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a8cdd015_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a8cdd015_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325193197"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/0237a870_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/0237a870_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/bf65248e_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/bf65248e_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/186c365d_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/186c365d_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/8a17d1b7_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/8a17d1b7_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/e36f158c_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/e36f158c_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/2a023b5b_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/2a023b5b_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/8350ac64_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/8350ac64_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/d549adcc_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/d549adcc_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/3e66e552_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/3e66e552_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/063cf7ff_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/063cf7ff_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/6e2d9295_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/6e2d9295_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/d3d83dbb_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/d3d83dbb_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325410506"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/795d5d87_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/795d5d87_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325410506"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/10d491f0_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/10d491f0_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325410506"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/dec72102_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/dec72102_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325410506"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/53a75a3c_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/53a75a3c_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325410506"
					]
				},
				{
					"caption": "Room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/13ab9d59_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/13ab9d59_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325410506"
					]
				},
				{
					"caption": "View from room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f16f2978_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f16f2978_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325193197"
					]
				},
				{
					"caption": "View from room",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/e177aad2_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/e177aad2_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c67fef30_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c67fef30_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325193197"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/957dfe96_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/957dfe96_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325193197"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/71d2cdf1_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/71d2cdf1_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325193197"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f3e3ac34_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f3e3ac34_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325193197"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a5b34c79_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a5b34c79_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070",
						"325193197"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/339662a2_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/339662a2_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070",
						"325193197"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/53eb365d_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/53eb365d_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070",
						"325193197"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f8b7f217_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f8b7f217_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/74500771_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/74500771_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070",
						"325193197"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/871fc444_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/871fc444_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070",
						"325193197"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/38e1b361_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/38e1b361_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325267070"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/3b7fac4d_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/3b7fac4d_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325410506"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a485a3b6_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a485a3b6_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325410506"
					]
				},
				{
					"caption": "Bathroom",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/bb0bd5ca_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/bb0bd5ca_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325410506"
					]
				},
				{
					"caption": "Interior",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/31bf3392_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/31bf3392_z.jpg",
							"href": ""
						}
					],
					"roomId": []
				},
				{
					"caption": "Interior",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/7bf31c52_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/7bf31c52_z.jpg",
							"href": ""
						}
					],
					"roomId": []
				},
				{
					"caption": "Interior",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/4536f6ad_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/4536f6ad_z.jpg",
							"href": ""
						}
					],
					"roomId": []
				},
				{
					"caption": "Interior",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/385f3f0f_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/385f3f0f_z.jpg",
							"href": ""
						}
					],
					"roomId": []
				},
				{
					"caption": "Interior",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/12a58ee7_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/12a58ee7_z.jpg",
							"href": ""
						}
					],
					"roomId": []
				},
				{
					"caption": "Front of property",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/dfaccb95_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/dfaccb95_z.jpg",
							"href": ""
						}
					],
					"roomId": []
				},
				{
					"caption": "City view",
					"category": "",
					"links": [
						{
							"size": "Standard",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c4d953b4_b.jpg",
							"href": ""
						},
						{
							"size": "XXL",
							"providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c4d953b4_z.jpg",
							"href": ""
						}
					],
					"roomId": [
						"325410506"
					]
				}
			]
		}
	}
}

Note - hotelId is the one to be taken from hotel APIs respective hotel object vervotechHotelId. 

================================================================================

6) Room details documentation ->

endpoint - /api/v1/room/getRoomDetails

request ->
{
	"autoSuggestId": "321f5a32-9b8b-4a72-b84c-da13a613da8f",
	"filterBySupplier": [], //GRNConnect, TBO, Booking, etc, keep it empty
	"hotelId": "16282095",
	"searchKey": "12fd7691-a190-42da-a8dc-18631a482d18"
}

response - 
{
  "success": true,
  "status": 0,
  "message": "Room details fetched successfully",
  "autoSuggestId": "321f5a32-9b8b-4a72-b84c-da13a613da8f",
  "searchKey": "12fd7691-a190-42da-a8dc-18631a482d18",
  "roomData": {
    "hotelId": "16282095",
    "standardRooms": [
      {
        "description": "Deluxe Double Room",
        "standardName": "Deluxe Double Room",
        "masterTitle": "Deluxe Double Room",
        "category": "Deluxe",
        "view": "",
        "roomLocation": "",
        "occupancyType": "1 Double",
        "roomRates": [
          {
            "roomId": "eyJyYXRlX2tleSI6IjRkaGZobWJyNHVxc3p3czN2Mm1na2dneDVoaTI1c2ZwN2c3NjV3MzczYmRiYjZwbmNwbXhsYmh3ZWFnYzcyaGx1bmlkcGJuN3RlZHZncWxldXd6c2MyZ3h0NnJ3am11czM3cXh6dzRhNGdudmZiY2Z0YXV3YW9rZGZ5IiwiY2l0eV9jb2RlIjoiMTI0MDU0Iiwicm9vbUNvZGUiOiI0ZGhmM3BqaTR5dXN0dWMzM3hzcWsiLCJncm91cENvZGUiOiJ3c2RianlsY3huNHVmZ2FhNHRiZGc0dXd4b2M0YmZ4a3Z3NzZwdTN5M3JhYjc2N2RjcGpxIiwicm9vbV9yZWZyZWNlIjoiNGRjZjVuYjQ1YXJjcHdrdHVnbmc0aHd4NWhrMmxzNWw3a3pvNXVkcTN6YnJ0NXhhbTJkY2hxdnpveW92M3BuZXU0Znd4Zm81c2ptYXMifQ==",
            "inputIndex": 61,
            "bed_group": [],
            "providerInfo": {
              "providerName": "GRNConnect",
              "providerHotelID": "1394865",
              "fareType": "MARKETFARE",
              "inPolicy": null,
              "outPolicyReasons": [],
              "ruleName": null,
              "outPolicyReasonKey": []
            },
            "amenities": [
              {
                "id": "",
                "name": "Free WiFi",
                "masterFacilityId": ""
              },
              {
                "id": "",
                "name": "Free self parking",
                "masterFacilityId": ""
              }
            ],
            "rateId": "eyJyYXRlX2tleSI6IjRkaGZobWJyNHVxc3p3czN2Mm1na2dneDVoaTI1c2ZwN2c3NjV3MzczYmRiYjZwbmNwbXhsYmh3ZWFnYzcyaGx1bmlkcGJuN3RlZHZncWxldXd6c2MyZ3h0NnJ3am11czM3cXh6dzRhNGdudmZiY2Z0YXV3YW9rZGZ5IiwiY2l0eV9jb2RlIjoiMTI0MDU0Iiwicm9vbUNvZGUiOiI0ZGhmM3BqaTR5dXN0dWMzM3hzcWsiLCJncm91cENvZGUiOiJ3c2RianlsY3huNHVmZ2FhNHRiZGc0dXd4b2M0YmZ4a3Z3NzZwdTN5M3JhYjc2N2RjcGpxIiwicm9vbV9yZWZyZWNlIjoiNGRjZjVuYjQ1YXJjcHdrdHVnbmc0aHd4NWhrMmxzNWw3a3pvNXVkcTN6YnJ0NXhhbTJkY2hxdnpveW92M3BuZXU0Znd4Zm81c2ptYXMifQ==",
            "totalPrice": {
              "source": "1353.0",
              "parsedValue": 1353
            },
            "basePrice": 1099.41,
            "taxes": 252.97,
            "taxBreakup": [
              {
                "amount": 38.59,
                "currency": null,
                "type": "GST"
              },
              {
                "amount": 214.38,
                "currency": null,
                "type": "Service Fee"
              }
            ],
            "searchId": "vne6tlmiu2edl4a6es62lj4gpi",
            "boardBasis": "",
            "refundability": "Non-Refundable",
            "cancelPenalties": [
              {
                "name": "Cancellation Policy",
                "penaltyDescription": "Non-Refundable",
                "nonRefundable": true
              }
            ]
          }
        ],
        "images": {
          "isDummy": true,
          "data": [
            {
              "caption": "Primary image",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/fccc6ac0_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/fccc6ac0_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c393849c_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c393849c_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a9e29d4e_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a9e29d4e_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/1e8105cf_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/1e8105cf_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a3c98683_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a3c98683_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/9ff01583_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/9ff01583_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a8cdd015_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a8cdd015_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/0237a870_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/0237a870_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/bf65248e_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/bf65248e_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/186c365d_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/186c365d_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/8a17d1b7_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/8a17d1b7_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/e36f158c_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/e36f158c_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/2a023b5b_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/2a023b5b_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/8350ac64_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/8350ac64_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/d549adcc_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/d549adcc_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/3e66e552_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/3e66e552_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/063cf7ff_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/063cf7ff_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/6e2d9295_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/6e2d9295_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/d3d83dbb_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/d3d83dbb_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/795d5d87_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/795d5d87_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/10d491f0_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/10d491f0_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/dec72102_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/dec72102_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/53a75a3c_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/53a75a3c_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/13ab9d59_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/13ab9d59_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "View from room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f16f2978_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f16f2978_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "View from room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/e177aad2_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/e177aad2_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c67fef30_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c67fef30_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/957dfe96_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/957dfe96_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/71d2cdf1_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/71d2cdf1_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f3e3ac34_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f3e3ac34_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a5b34c79_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a5b34c79_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070",
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/339662a2_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/339662a2_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070",
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/53eb365d_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/53eb365d_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070",
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f8b7f217_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f8b7f217_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/74500771_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/74500771_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070",
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/871fc444_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/871fc444_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070",
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/38e1b361_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/38e1b361_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/3b7fac4d_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/3b7fac4d_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a485a3b6_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a485a3b6_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/bb0bd5ca_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/bb0bd5ca_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "City view",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c4d953b4_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c4d953b4_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            }
          ]
        }
      },
      {
        "description": "Standard Room",
        "standardName": "Standard Room",
        "masterTitle": "Standard Room",
        "category": "Standard",
        "view": "",
        "roomLocation": "",
        "occupancyType": "",
        "roomRates": [],
        "images": {
          "isDummy": true,
          "data": [
            {
              "caption": "Primary image",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/fccc6ac0_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/fccc6ac0_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c393849c_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c393849c_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a9e29d4e_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a9e29d4e_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/1e8105cf_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/1e8105cf_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a3c98683_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a3c98683_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/9ff01583_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/9ff01583_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a8cdd015_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a8cdd015_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/0237a870_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/0237a870_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/bf65248e_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/bf65248e_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/186c365d_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/186c365d_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/8a17d1b7_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/8a17d1b7_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/e36f158c_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/e36f158c_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/2a023b5b_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/2a023b5b_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/8350ac64_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/8350ac64_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/d549adcc_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/d549adcc_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/3e66e552_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/3e66e552_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/063cf7ff_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/063cf7ff_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/6e2d9295_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/6e2d9295_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/d3d83dbb_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/d3d83dbb_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/795d5d87_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/795d5d87_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/10d491f0_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/10d491f0_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/dec72102_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/dec72102_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/53a75a3c_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/53a75a3c_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/13ab9d59_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/13ab9d59_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "View from room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f16f2978_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f16f2978_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "View from room",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/e177aad2_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/e177aad2_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c67fef30_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c67fef30_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/957dfe96_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/957dfe96_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/71d2cdf1_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/71d2cdf1_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f3e3ac34_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f3e3ac34_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a5b34c79_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a5b34c79_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070",
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/339662a2_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/339662a2_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070",
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/53eb365d_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/53eb365d_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070",
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f8b7f217_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/f8b7f217_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/74500771_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/74500771_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070",
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/871fc444_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/871fc444_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070",
                "325193197"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/38e1b361_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/38e1b361_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325267070"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/3b7fac4d_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/3b7fac4d_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a485a3b6_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/a485a3b6_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "Bathroom",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/bb0bd5ca_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/bb0bd5ca_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            },
            {
              "caption": "City view",
              "category": "",
              "links": [
                {
                  "size": "Standard",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c4d953b4_b.jpg",
                  "href": ""
                },
                {
                  "size": "XXL",
                  "providerHref": "https://i.travelapi.com/lodging/108000000/107480000/107478000/107477910/c4d953b4_z.jpg",
                  "href": ""
                }
              ],
              "roomId": [
                "325410506"
              ]
            }
          ]
        }
      }
    ]
  }
}









