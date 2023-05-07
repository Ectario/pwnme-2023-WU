## XOR Function
ORIGINAL_MESSAGE ^ SECRET = ENCRYPTED_MESSAGE

The xor also works in all other directions, for example:
ORIGINAL_MESSAGE ^ ENCRYPTED_MESSAGE = SECRET
ENCRYPTED_MESSAGE ^ SECRET = ORIGINAL_MESSAGE

## Information available to us

ENCRYPTED_MESSAGE
SECRET: Random string of 16 characters
MESSAGE_ORIGINAL: Parts of the message

## Analysis

In order to encrypt the message, a secret is generated. This 16-character secret is used cyclically.
It will be repeated in order to encrypt the whole message

Example:

```
SECRET: HELLO
MESSAGE_ORIGINAL: FLAG{super_secret}
```

In order to make the same size as the original message, the secret becomes:
`HELLOHELLOHELLOHEL`

And will thus be able to xor our original message:

`HELLOHELLOHELLOHEL ^ FLAG{super_secret} = MESSAGEXORENCRYPT`

Here, the secret is a string of 5 characters.

As seen previously, the xor can be done in all directions. So if we know 1 character of the original message and we have the encrypted message, we can find 1 character of the secret.

Example:

```
We know 1 characters of the original message

ENCRYPTED_MESSAGE = MESSAGEXORENCRYPTED
MESSAGE_ORIGINAL = F****************

F^M=H

We were therefore able to recover the 1st character of our HELLO secret: the H.
Knowing that the secret is cyclical, we can start to reconstruct the whole secret:

H****H****H****H**

In order to complete the secret, we now need the characters in position 2, 3, 4 and 5

If we have the character in position 7 (or 2, or 12..), we can have the 2nd character of the secret
ENCRYPTED_MESSAGE = MESSAGEXORENCRYPTED
MESSAGE_ORIGINAL = F*****u***********

u^E=E
HE***HE***HE***HE*
```

## Solution

In this challenge, the clue is perfectly created so that we can find all the characters of the secret.

```
Cutting the clue into blocks, the size of the secret

**,** **not*******
****** *** *****
***s******ra***
****not***********
 y******g***W**
****************
****************
******k******h*
****************
```

We have all the characters needed to reconstruct the secret