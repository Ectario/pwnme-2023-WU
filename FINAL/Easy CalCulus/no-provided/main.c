#include <openssl/ec.h>
#include <openssl/obj_mac.h>
#include <string.h>
#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <stdlib.h>

typedef unsigned int uint; 

typedef struct POINT_INFO {
    char* begin_x;
    char* end_x;
    char* begin_y;
    char* end_y;
} POINT_INFO;

char* begin_x = "65485170049033141755572552932091555";
char* end_x = "440395722142984193594072873483228125624049";
char* begin_y = "7316337776303114103250125977973844109424";
char* end_y = "7887834941211187427503803434828368457";

void __attribute((constructor)) init_buffer()
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

void timer_handler(int signum) {
    printf("Time's up! It's probably not me, I'm too smart to hesitate...\n");
    exit(0);
}

BIGNUM* generate_test(EC_POINT* test, EC_KEY* key, BIGNUM* x_gen, BIGNUM* y_gen, POINT_INFO* generator_info,  uint* size_max){
    EC_POINT* point = EC_POINT_new(EC_KEY_get0_group(key));
    int length_begin = strlen(generator_info->begin_x);
    int length_end = strlen(generator_info->end_x);
    char x[length_begin + length_end];
    x[0] = 0;
    strncat(x, generator_info->begin_x, length_begin);
    strncat(x, generator_info->end_x, length_end);
    BN_dec2bn(&x_gen, x);
    length_begin = strlen(generator_info->begin_y);
    length_end = strlen(generator_info->end_y);
    char y[length_begin + length_end];
    y[0] = 0;
    strncat(y, generator_info->begin_y, length_begin);
    strncat(y, generator_info->end_y, length_end);
    BN_dec2bn(&y_gen, y);
    EC_POINT_set_affine_coordinates_GFp(EC_KEY_get0_group(key), point, x_gen, y_gen, NULL);

    BIGNUM* random_value = BN_new();
    BN_rand(random_value, 224, -1, 0);
    char* random_value_str = BN_bn2hex(random_value);
    printf("Hint for the test: %s\n", random_value_str);
    *size_max = strlen(random_value_str)*5;

    EC_POINT_mul(EC_KEY_get0_group(key), test, NULL, point, random_value, NULL);

    EC_POINT_free(point);
    free(random_value_str);
    return random_value;
}

int test_checking(EC_POINT* test, EC_KEY* key, BIGNUM* x_gen, BIGNUM* y_gen, POINT_INFO* generator_info, BIGNUM* input){
    EC_POINT* point = EC_POINT_new(EC_KEY_get0_group(key));

    EC_POINT_set_affine_coordinates_GFp(EC_KEY_get0_group(key), point, x_gen, y_gen, NULL);

    EC_POINT* try = EC_POINT_new(EC_KEY_get0_group(key));
    EC_POINT_mul(EC_KEY_get0_group(key), try, NULL, point, input, NULL);

    // Compare the two points
    int cmp_result = EC_POINT_cmp(EC_KEY_get0_group(key), test, try, NULL);

    // freeing
    EC_POINT_free(point);
    EC_POINT_free(try);

    return cmp_result;
}

int main() {
    EC_KEY* key = EC_KEY_new_by_curve_name(NID_secp256k1);
    EC_POINT* test = EC_POINT_new(EC_KEY_get0_group(key));
    BIGNUM* x_gen = BN_new();
    BIGNUM* y_gen = BN_new();
    POINT_INFO generator;
    generator.begin_x = begin_x;
    generator.end_x = end_x;
    generator.begin_y = begin_y;
    generator.end_y = end_y;
    uint size_max;

    BIGNUM* already_used_value = generate_test(test, key, x_gen, y_gen, &generator, &size_max);

    struct sigaction sa;
    sa.sa_handler = timer_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGALRM, &sa, NULL);
    alarm(3);

    printf("Surprise! this is a test, gib me the value that I want: \n");
    BIGNUM* input = BN_new();
    char inp[size_max];
    fgets(inp, size_max, stdin);
    BN_dec2bn(&input, inp);

    int cmp = BN_cmp(input, already_used_value);
    if(cmp == 0){
        printf("Nice, now I know that you know how to read hoho! (yea' this is a fun sentence)\n");
        exit(0);
    }

    int cmp_result = test_checking(test, key, x_gen, y_gen, &generator, input);

    if (cmp_result == 0) {
        printf("Ho yeaaah it feels good to be so smaaaart\n");
        printf("I'm so confident that I can tell this: ");
        FILE *file;
        char buffer[100];
        file = fopen("flag.txt", "r");
        if (file == NULL) {
            printf("Failed to open the file.\n");
            return 1;
        }
        size_t bytesRead = fread(buffer, sizeof(char), sizeof(buffer) - 1, file);
        if (bytesRead == 0) {
            printf("Failed to read the file.\n");
            fclose(file); 
            return 1; 
        }
        buffer[bytesRead] = '\0';
        fclose(file);
        printf("%s\n", buffer);
    } else {
        printf("Haha my big smart brain can't be broken with someone like you\n");
    }

    // Clean up and free memory
    EC_POINT_free(test);
    EC_KEY_free(key);
    BN_free(x_gen);
    BN_free(y_gen);
    BN_free(already_used_value);
    
    return 0;
}
