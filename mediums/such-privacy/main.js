const { CURVE, Point } = require('@noble/secp256k1');
const { BigNumber } = require('ethers');
const { keccak256, arrayify, getAddress, hexDataSlice } = require('ethers/lib/utils');
const {writeFileSync} = require('fs');

(async () => {
    writeFileSync('hint.json', JSON.stringify(new Array(5).fill(true).map(Math.random), null, 2), {encoding: 'utf-8'});
    const seedKey = arrayify(BigNumber.from(keccak256(Math.floor(Math.random() * Number.MAX_SAFE_INTEGER))).add(BigNumber.from('0x260026002600260026002600').mul(0x2600n)).mod(CURVE.n));
    let newPoint = Point.fromPrivateKey(seedKey);
    
    for (let i = 1; ; i++) {
        newPoint = newPoint.add(Point.BASE);
        const newAddress = hexDataSlice(keccak256(hexDataSlice('0x' + newPoint.toHex(), 1)), 12);
        if (newAddress.startsWith('0x2600')) {
            return void writeFileSync('flag.json', JSON.stringify({
                privateKey: BigNumber.from(seedKey).add(i).toHexString(),
                publicKey: getAddress(newAddress)
            }, null, '\t\v\n\r\f'), {encoding: 'utf-8'});
        }
      }
})();